import os
import sys
import subprocess

# Auto-detect virtual environment in backend/.venv if required packages are missing
try:
    import pandas
    import yaml
    import sqlalchemy
except ImportError:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.abspath(os.path.join(base_dir, "..", ".venv", "Scripts", "python.exe"))
    if os.path.exists(venv_python) and sys.executable != venv_python:
        result = subprocess.run([venv_python] + sys.argv)
        sys.exit(result.returncode)
    else:
        print("Error: Required packages (pandas, pyyaml, sqlalchemy) not found.")
        print("Please activate the virtual environment: cd backend && .\\.venv\\Scripts\\activate")
        sys.exit(1)

import json
import argparse
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Ensure parent backend directory is on sys.path for database imports
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database.connection import LocalSessionLocal, SupabaseSessionLocal, local_engine, LocalBase, SupabaseBase, settings
from app.database.models import PriceHistory, MarketPrice, DatasetManifest
from config import ConfigLoader
from logger import setup_logger
from validator import DataValidator

def parse_args():
    parser = argparse.ArgumentParser(description="Market Data Importer to Database (CSV -> Validate -> Normalize -> Insert -> Supabase)")
    parser.add_argument("--symbol", "-s", type=str, nargs="+", help="Symbol(s) to import")
    parser.add_argument("--timeframe", "-t", type=str, nargs="+", help="Timeframe(s) to import")
    parser.add_argument("--config", "-c", type=str, help="Custom settings.yaml path")
    return parser.parse_args()

class DataImporter:
    """
    Importer Pipeline:
    CSV ──► Validate ──► Normalize ──► Insert ──► Supabase
    """
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path)
        log_file = os.path.join(self.config.output_dir, "importer.log")
        self.logger = setup_logger("market_data_importer", log_file=log_file)
        self.validator = DataValidator(config_path)
        
        # Ensure database tables exist for both Local and Cloud fallback
        LocalBase.metadata.create_all(bind=local_engine)
        SupabaseBase.metadata.create_all(bind=local_engine)

    def import_symbol_timeframe(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        tf_str = timeframe.upper()
        sym_str = symbol.upper()
        csv_path = os.path.join(self.config.output_dir, sym_str, f"{tf_str}.csv")
        
        # STAGE 1: LOAD CSV
        df = self._stage_1_load_csv(csv_path, sym_str, tf_str)
        if df is None or df.empty:
            return {"symbol": sym_str, "timeframe": tf_str, "status": "EMPTY_OR_MISSING", "imported_rows": 0}

        # STAGE 2: VALIDATE
        df_valid, val_report = self._stage_2_validate(csv_path, tf_str)

        # STAGE 3: NORMALIZE
        df_norm = self._stage_3_normalize(df_valid, sym_str, tf_str)

        # STAGE 4 & 5: INSERT INTO LOCAL DB & SUPABASE
        new_count = self._stage_4_5_insert_and_sync(df_norm, sym_str, tf_str, val_report)

        return {
            "symbol": sym_str,
            "timeframe": tf_str,
            "total_rows": len(df_norm),
            "new_records_imported": new_count,
            "health_score": val_report.get("health_score", 100.0),
            "status": "SUCCESS"
        }

    def _stage_1_load_csv(self, csv_path: str, symbol: str, timeframe: str) -> pd.DataFrame:
        """Stage 1: Load raw CSV file."""
        if not os.path.exists(csv_path):
            self.logger.warning(f"[STAGE 1 LOAD] CSV file not found: {csv_path}")
            return None

        self.logger.info(f"[STAGE 1 LOAD] Loading dataset: {symbol} ({timeframe}) from {csv_path}")
        df = pd.read_csv(csv_path)
        return df

    def _stage_2_validate(self, csv_path: str, timeframe: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Stage 2: Validate OHLC logic, drop duplicates, check gaps."""
        self.logger.info(f"[STAGE 2 VALIDATE] Running Data Quality Validation for {os.path.basename(csv_path)}...")
        df_clean, val_report = self.validator.validate_file(csv_path, timeframe)
        self.logger.info(f"[STAGE 2 VALIDATE] Quality Score: {val_report.get('health_score')}% | Clean Rows: {len(df_clean)}")
        return df_clean, val_report

    def _stage_3_normalize(self, df: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
        """Stage 3: Normalize timestamps to UTC, cast data types, round precisions."""
        self.logger.info(f"[STAGE 3 NORMALIZE] Normalizing data types, UTC timestamps & price precision...")
        df_norm = df.copy()

        # Timestamp UTC normalization
        df_norm['timestamp'] = pd.to_datetime(df_norm['timestamp'])
        if df_norm['timestamp'].dt.tz is not None:
            df_norm['timestamp'] = df_norm['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)

        # Precision & Numeric Normalization
        df_norm['open'] = df_norm['open'].astype(float).round(5)
        df_norm['high'] = df_norm['high'].astype(float).round(5)
        df_norm['low'] = df_norm['low'].astype(float).round(5)
        df_norm['close'] = df_norm['close'].astype(float).round(5)
        df_norm['volume'] = df_norm['volume'].astype(float).round(2)
        df_norm['spread'] = df_norm['spread'].astype(float).round(2)

        # Sort chronological
        df_norm = df_norm.sort_values(by='timestamp').reset_index(drop=True)
        return df_norm

    def _stage_4_5_insert_and_sync(self, df: pd.DataFrame, symbol: str, timeframe: str, val_report: Dict[str, Any]) -> int:
        """Stage 4 & 5: Execute Bulk Insert/Upsert to Local Database & Supabase Cloud."""
        self.logger.info(f"[STAGE 4 INSERT] Bulk inserting dataset into Local DB & Supabase Cloud...")
        
        # 1. Local SQLite Bulk Insert
        db_local = LocalSessionLocal()
        new_records_count = 0
        try:
            existing_ts_set = set(
                ts[0] for ts in db_local.query(PriceHistory.timestamp).filter(
                    PriceHistory.symbol == symbol,
                    PriceHistory.timeframe == timeframe
                ).all()
            )

            records_to_insert = []
            for _, row in df.iterrows():
                ts_val = row['timestamp'].to_pydatetime()
                if ts_val not in existing_ts_set:
                    records_to_insert.append(PriceHistory(
                        symbol=symbol,
                        timeframe=timeframe,
                        timestamp=ts_val,
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume']),
                        spread=float(row['spread'])
                    ))

            if records_to_insert:
                db_local.bulk_save_objects(records_to_insert)
                db_local.commit()
                new_records_count = len(records_to_insert)
                self.logger.info(f"[STAGE 4 INSERT] Ingested {new_records_count} new records into Local DB.")
            else:
                self.logger.info(f"[STAGE 4 INSERT] All {len(df)} records already synced in Local DB.")
        except Exception as e:
            db_local.rollback()
            self.logger.error(f"[STAGE 4 INSERT] Error saving to Local DB: {e}")
        finally:
            db_local.close()

        # 2. Supabase Cloud Sync (Stage 5)
        if settings.USE_SUPABASE and SupabaseSessionLocal:
            self.logger.info(f"[STAGE 5 SUPABASE] Syncing dataset to Supabase Cloud PostgreSQL...")
            db_cloud = SupabaseSessionLocal()
            try:
                cloud_ts_set = set(
                    ts[0] for ts in db_cloud.query(MarketPrice.timestamp).filter(
                        MarketPrice.symbol == symbol,
                        MarketPrice.timeframe == timeframe
                    ).all()
                )
                cloud_inserts = []
                for _, row in df.iterrows():
                    ts_val = row['timestamp'].to_pydatetime()
                    if ts_val not in cloud_ts_set:
                        cloud_inserts.append(MarketPrice(
                            symbol=symbol,
                            timeframe=timeframe,
                            timestamp=ts_val,
                            open=float(row['open']),
                            high=float(row['high']),
                            low=float(row['low']),
                            close=float(row['close']),
                            volume=float(row['volume']),
                            spread=float(row['spread'])
                        ))

                if cloud_inserts:
                    db_cloud.bulk_save_objects(cloud_inserts)
                    db_cloud.commit()
                    self.logger.info(f"[STAGE 5 SUPABASE] Uploaded {len(cloud_inserts)} new records to Supabase Cloud.")
            except Exception as ce:
                db_cloud.rollback()
                self.logger.error(f"[STAGE 5 SUPABASE] Error syncing to Supabase Cloud: {ce}")
            finally:
                db_cloud.close()

        # 3. Update Dataset Manifest Entry
        start_time = df['timestamp'].iloc[0].to_pydatetime() if len(df) > 0 else None
        end_time = df['timestamp'].iloc[-1].to_pydatetime() if len(df) > 0 else None
        health_score = val_report.get("health_score", 100.0)

        db_manifest = LocalSessionLocal()
        try:
            manifest_entry = db_manifest.query(DatasetManifest).filter(
                DatasetManifest.symbol == symbol,
                DatasetManifest.timeframe == timeframe
            ).first()

            if not manifest_entry:
                manifest_entry = DatasetManifest(
                    symbol=symbol,
                    timeframe=timeframe,
                    total_bars=len(df),
                    start_time=start_time,
                    end_time=end_time,
                    health_score=health_score,
                    last_imported_at=datetime.now()
                )
                db_manifest.add(manifest_entry)
            else:
                manifest_entry.total_bars = len(df)
                manifest_entry.start_time = start_time
                manifest_entry.end_time = end_time
                manifest_entry.health_score = health_score
                manifest_entry.last_imported_at = datetime.now()

            db_manifest.commit()
            self.logger.info(f"[STAGE 5 SUPABASE] Catalog Manifest updated for {symbol} ({timeframe})")
        except Exception as me:
            db_manifest.rollback()
            self.logger.error(f"Error updating dataset manifest: {me}")
        finally:
            db_manifest.close()

        return new_records_count

    def import_all(self, symbols: List[str] = None, timeframes: List[str] = None) -> List[Dict[str, Any]]:
        target_symbols = symbols or self.config.symbols
        target_timeframes = timeframes or self.config.timeframes

        self.logger.info("=" * 70)
        self.logger.info("STARTING IMPORTER PIPELINE")
        self.logger.info("Pipeline: CSV ──► Validate ──► Normalize ──► Insert ──► Supabase")
        self.logger.info(f"Target Symbols: {target_symbols} | Timeframes: {target_timeframes}")
        self.logger.info("=" * 70)

        results = []
        for symbol in target_symbols:
            for tf in target_timeframes:
                res = self.import_symbol_timeframe(symbol, tf)
                results.append(res)

        self.logger.info("=" * 70)
        self.logger.info("IMPORTER PIPELINE COMPLETED")
        self.logger.info("=" * 70)
        return results

def main():
    args = parse_args()
    importer = DataImporter(config_path=args.config)
    importer.import_all(symbols=args.symbol, timeframes=args.timeframe)

if __name__ == "__main__":
    main()
