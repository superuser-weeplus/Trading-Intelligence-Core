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

import argparse
from typing import List, Dict, Any

# Ensure package directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import ConfigLoader
from logger import setup_logger
from exporter import MarketDataExporter
from validator import DataValidator
from importer import DataImporter

def parse_args():
    parser = argparse.ArgumentParser(
        description="Master Market Data Pipeline (MT5 -> Exporter -> Validator -> Importer -> Supabase)"
    )
    parser.add_argument("--symbol", "-s", type=str, nargs="+", help="Symbol(s) to process")
    parser.add_argument("--timeframe", "-t", type=str, nargs="+", help="Timeframe(s) to process")
    parser.add_argument("--bars", "-b", type=int, help="Number of bars to fetch")
    parser.add_argument("--format", "-f", type=str, nargs="+", help="Export format(s): csv, json, parquet")
    parser.add_argument("--config", "-c", type=str, help="Custom settings.yaml path")
    return parser.parse_args()

class MarketDataPipeline:
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path)
        log_file = os.path.join(self.config.output_dir, "pipeline.log")
        self.logger = setup_logger("market_data_pipeline", log_file=log_file)
        
        self.exporter = MarketDataExporter(config_path)
        self.validator = DataValidator(config_path)
        self.importer = DataImporter(config_path)

    def run_pipeline(
        self,
        symbols: List[str] = None,
        timeframes: List[str] = None,
        bars: int = None,
        formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end data foundation pipeline:
        Stage 1: MT5 Exporter
        Stage 2: Data Quality Validator
        Stage 3: Database Importer (Supabase / SQLite)
        """
        target_symbols = symbols or self.config.symbols
        target_timeframes = timeframes or self.config.timeframes
        
        self.logger.info("=" * 70)
        self.logger.info("MARKET DATA PIPELINE (DATA FOUNDATION)")
        self.logger.info("Pipeline Flow: MT5 -> Exporter -> Validator -> Importer -> Supabase")
        self.logger.info(f"Symbols: {target_symbols} | Timeframes: {target_timeframes}")
        self.logger.info("=" * 70)

        # STAGE 1: EXPORTER
        self.logger.info("\n>>> STAGE 1: MT5 Market Data Exporter")
        export_results = self.exporter.run_export(
            symbols=target_symbols,
            timeframes=target_timeframes,
            bars=bars,
            formats=formats
        )

        # STAGE 2: VALIDATOR
        self.logger.info("\n>>> STAGE 2: Data Quality Validator")
        validation_reports = self.validator.validate_all(
            symbols=target_symbols,
            timeframes=target_timeframes
        )

        # STAGE 3: IMPORTER
        self.logger.info("\n>>> STAGE 3: Database Importer (Supabase Cloud / Local Database)")
        import_results = self.importer.import_all(
            symbols=target_symbols,
            timeframes=target_timeframes
        )

        # SUMMARY REPORT
        self.logger.info("\n" + "=" * 70)
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Stage 1 Exporter Tasks: {sum(1 for r in export_results if r.success)}/{len(export_results)} Passed")
        self.logger.info(f"Stage 2 Validation Reports: {len(validation_reports)} Generated")
        self.logger.info(f"Stage 3 Database Imports: {sum(1 for r in import_results if r['status'] == 'SUCCESS')}/{len(import_results)} Ingested")
        self.logger.info("=" * 70)

        return {
            "export_results": export_results,
            "validation_reports": validation_reports,
            "import_results": import_results
        }

def main():
    args = parse_args()
    pipeline = MarketDataPipeline(config_path=args.config)
    pipeline.run_pipeline(
        symbols=args.symbol,
        timeframes=args.timeframe,
        bars=args.bars,
        formats=args.format
    )

if __name__ == "__main__":
    main()
