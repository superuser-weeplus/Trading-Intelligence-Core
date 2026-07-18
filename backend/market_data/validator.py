import os
import sys
import subprocess

# Auto-detect virtual environment in backend/.venv if required packages are missing
try:
    import pandas
    import yaml
except ImportError:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.abspath(os.path.join(base_dir, "..", ".venv", "Scripts", "python.exe"))
    if os.path.exists(venv_python) and sys.executable != venv_python:
        result = subprocess.run([venv_python] + sys.argv)
        sys.exit(result.returncode)
    else:
        print("Error: Required packages (pandas, pyyaml) not found.")
        print("Please activate the virtual environment: cd backend && .\\.venv\\Scripts\\activate")
        sys.exit(1)

import json
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Ensure package directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import ConfigLoader
from logger import setup_logger
from utils import ensure_directory

def parse_args():
    parser = argparse.ArgumentParser(description="Market Data Quality Validator")
    parser.add_argument("--symbol", "-s", type=str, nargs="+", help="Symbol(s) to validate")
    parser.add_argument("--timeframe", "-t", type=str, nargs="+", help="Timeframe(s) to validate")
    parser.add_argument("--config", "-c", type=str, help="Custom settings.yaml path")
    return parser.parse_args()

class DataValidator:
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path)
        log_file = os.path.join(self.config.output_dir, "validator.log")
        self.logger = setup_logger("market_data_validator", log_file=log_file)

    def validate_file(self, file_path: str, timeframe: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Validates a single market data CSV/JSON file.
        Returns cleaned DataFrame and validation report dictionary.
        """
        self.logger.info(f"Validating file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Load file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported format for validation. Use .csv or .json")

        if df.empty:
            return df, {"status": "EMPTY", "health_score": 0.0, "total_rows": 0}

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        initial_rows = len(df)
        
        report = {
            "file": os.path.basename(file_path),
            "timeframe": timeframe.upper(),
            "initial_rows": initial_rows,
            "ohlc_errors": 0,
            "duplicate_rows_removed": 0,
            "spike_anomalies": 0,
            "missing_gaps_detected": 0,
            "final_clean_rows": initial_rows,
            "health_score": 100.0,
            "status": "PASSED"
        }

        # 1. OHLC Logic Integrity Check
        invalid_ohlc_mask = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close']) |
            (df['open'] <= 0) |
            (df['high'] <= 0) |
            (df['low'] <= 0) |
            (df['close'] <= 0) |
            (df['volume'] < 0)
        )
        ohlc_errors = int(invalid_ohlc_mask.sum())
        report["ohlc_errors"] = ohlc_errors

        # Filter out invalid OHLC rows
        if ohlc_errors > 0:
            self.logger.warning(f"Found {ohlc_errors} OHLC logical error rows in {file_path}")
            df = df[~invalid_ohlc_mask].copy()

        # 2. Duplicate Timestamps Check
        initial_before_dup = len(df)
        df = df.drop_duplicates(subset=['timestamp'], keep='last').copy()
        duplicates_removed = initial_before_dup - len(df)
        report["duplicate_rows_removed"] = duplicates_removed
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate timestamp rows.")

        # Sort chronologically
        df = df.sort_values(by='timestamp').reset_index(drop=True)

        # 3. Spike / Extreme Outlier Detection (>15% candle move)
        price_change_pct = (df['close'] - df['open']).abs() / df['open']
        spikes_mask = price_change_pct > 0.15
        spikes_count = int(spikes_mask.sum())
        report["spike_anomalies"] = spikes_count
        if spikes_count > 0:
            self.logger.warning(f"Detected {spikes_count} extreme price spike anomalies (>15% single bar move)")

        # 4. Missing Gap Detection
        tf_minutes_map = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        expected_step = timedelta(minutes=tf_minutes_map.get(timeframe.upper(), 60))
        
        if len(df) > 1:
            time_diffs = df['timestamp'].diff()
            # Flag gaps significantly larger than expected step (allowing for weekend gaps ~48h)
            gaps_mask = (time_diffs > expected_step * 2) & (time_diffs < timedelta(hours=72))
            report["missing_gaps_detected"] = int(gaps_mask.sum())

        # Final health score calculation
        report["final_clean_rows"] = len(df)
        penalty = (ohlc_errors * 2.0) + (duplicates_removed * 0.5) + (spikes_count * 1.0)
        report["health_score"] = round(max(0.0, 100.0 - penalty), 2)
        if report["health_score"] < 80.0:
            report["status"] = "NEEDS_ATTENTION"

        return df, report

    def validate_symbol(self, symbol: str, timeframes: List[str] = None) -> Dict[str, Any]:
        """
        Validates all timeframe files for a specific symbol directory.
        """
        sym_dir = os.path.join(self.config.output_dir, symbol.upper())
        if not os.path.exists(sym_dir):
            self.logger.warning(f"Directory for symbol {symbol} does not exist at {sym_dir}")
            return {}

        target_timeframes = timeframes or self.config.timeframes
        symbol_report = {
            "symbol": symbol.upper(),
            "validated_at": datetime.now().isoformat(),
            "timeframes": {}
        }

        for tf in target_timeframes:
            tf_str = tf.upper()
            csv_path = os.path.join(sym_dir, f"{tf_str}.csv")
            
            if os.path.exists(csv_path):
                clean_df, tf_report = self.validate_file(csv_path, tf_str)
                # Overwrite CSV with cleaned dataset
                clean_df.to_csv(csv_path, index=False)
                symbol_report["timeframes"][tf_str] = tf_report

        # Write symbol validation report
        report_path = os.path.join(sym_dir, "validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(symbol_report, f, indent=2)

        self.logger.info(f"Generated validation report for {symbol}: {report_path}")
        return symbol_report

    def validate_all(self, symbols: List[str] = None, timeframes: List[str] = None) -> List[Dict[str, Any]]:
        target_symbols = symbols or self.config.symbols
        self.logger.info("=" * 60)
        self.logger.info(f"Starting Data Quality Validation for {target_symbols}")
        self.logger.info("=" * 60)

        reports = []
        for symbol in target_symbols:
            rep = self.validate_symbol(symbol, timeframes)
            if rep:
                reports.append(rep)

        self.logger.info("Data Validation completed successfully.")
        return reports

def main():
    args = parse_args()
    validator = DataValidator(config_path=args.config)
    validator.validate_all(symbols=args.symbol, timeframes=args.timeframe)

if __name__ == "__main__":
    main()
