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

import argparse
from typing import List

# Ensure package directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import ConfigLoader
from logger import setup_logger
from mt5_client import MT5Client
from models import ExportRequest, ExportResult
from utils import ensure_directory, format_rates_dataframe, save_export_file, write_symbol_metadata, write_manifest

def parse_args():
    parser = argparse.ArgumentParser(
        description="MT5 Market Data Exporter for Trading Intelligence Core"
    )
    parser.add_argument(
        "--symbol", "-s",
        type=str,
        nargs="+",
        help="Symbol(s) to export (e.g. XAUUSD GBPUSD EURUSD DXY). If omitted, uses config defaults."
    )
    parser.add_argument(
        "--timeframe", "-t",
        type=str,
        nargs="+",
        help="Timeframe(s) to export (e.g. M1 M5 M15 H1 H4 D1). If omitted, uses config defaults."
    )
    parser.add_argument(
        "--bars", "-b",
        type=int,
        help="Number of historical candles/bars to fetch per timeframe. If omitted, uses config default (5000)."
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        nargs="+",
        help="Export format(s): csv, json, parquet. Default is ['csv', 'json']."
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to custom settings.yaml configuration file."
    )
    return parser.parse_parse_args() if hasattr(parser, 'parse_parse_args') else parser.parse_args()

class MarketDataExporter:
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path)
        log_file = os.path.join(self.config.output_dir, "exporter.log")
        self.logger = setup_logger("market_data_exporter", log_file=log_file)
        self.client = MT5Client(self.config.mt5_config)

    def run_export(
        self,
        symbols: List[str] = None,
        timeframes: List[str] = None,
        bars: int = None,
        formats: List[str] = None
    ) -> List[ExportResult]:
        """
        Executes batch export of market data files based on configuration or CLI inputs.
        """
        target_symbols = symbols or self.config.symbols
        target_timeframes = timeframes or self.config.timeframes
        target_bars = bars or self.config.default_bars
        target_formats = formats or self.config.export_formats

        self.logger.info("=" * 60)
        self.logger.info("Starting MT5 Market Data Exporter Batch Job")
        self.logger.info(f"Target Symbols: {target_symbols}")
        self.logger.info(f"Target Timeframes: {target_timeframes}")
        self.logger.info(f"Bars per request: {target_bars}")
        self.logger.info(f"Export Formats: {target_formats}")
        self.logger.info(f"Output Directory: {self.config.output_dir}")
        self.logger.info("=" * 60)

        results = []
        
        # Connect to MT5
        self.client.connect()

        try:
            for symbol in target_symbols:
                # Resolve broker symbol alias if mapped (e.g. XAUUSD -> XAUUSDc)
                mapped_symbol = self.config.resolve_symbol(symbol)
                
                # Output directory for this symbol: output/{symbol}/
                symbol_out_dir = os.path.join(self.config.output_dir, symbol.upper())
                ensure_directory(symbol_out_dir)

                for tf in target_timeframes:
                    tf_str = tf.upper()
                    self.logger.info(f"--- Exporting {symbol} ({tf_str}) ---")
                    
                    result = ExportResult(symbol=symbol, timeframe=tf_str, bars_fetched=0)
                    
                    try:
                        # Fetch rates via MT5Client
                        raw_rates = self.client.fetch_rates(mapped_symbol, tf_str, count=target_bars)
                        df = format_rates_dataframe(raw_rates)
                        
                        result.bars_fetched = len(df)
                        
                        if len(df) == 0:
                            self.logger.warning(f"No data returned for {symbol} ({tf_str}). Skipping file save.")
                            result.success = False
                            result.error_message = "Empty dataset returned"
                            results.append(result)
                            continue

                        result.start_time = df['timestamp'].iloc[0].strftime('%Y-%m-%dT%H:%M:%S')
                        result.end_time = df['timestamp'].iloc[-1].strftime('%Y-%m-%dT%H:%M:%S')

                        # Save into requested formats under output/{symbol}/{timeframe}.{ext}
                        file_base_path = os.path.join(symbol_out_dir, tf_str)
                        
                        for fmt in target_formats:
                            filepath = save_export_file(df, file_base_path, fmt)
                            result.saved_files.append(filepath)

                        result.success = True
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol} ({tf_str}): {e}")
                        result.success = False
                        result.error_message = str(e)

                    results.append(result)

                # Generate symbol metadata.json
                write_symbol_metadata(symbol, mapped_symbol, symbol_out_dir, results)

            # Generate root manifest.json
            write_manifest(self.config.output_dir, results)

        finally:
            self.client.disconnect()

        self._print_summary(results)
        return results

    def _print_summary(self, results: List[ExportResult]):
        self.logger.info("\n" + "=" * 60)
        self.logger.info("MARKET DATA EXPORT SUMMARY")
        self.logger.info("=" * 60)
        
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        for r in results:
            status = "SUCCESS" if r.success else "FAILED"
            files_str = ", ".join([os.path.basename(f) for f in r.saved_files])
            self.logger.info(f"[{status}] {r.symbol:<8} ({r.timeframe:<4}) -> {r.bars_fetched} bars | Files: {files_str}")

        self.logger.info("-" * 60)
        self.logger.info(f"Completed {success_count}/{total_count} export tasks successfully.")
        self.logger.info("=" * 60)

def main():
    args = parse_args()
    exporter = MarketDataExporter(config_path=args.config)
    exporter.run_export(
        symbols=args.symbol,
        timeframes=args.timeframe,
        bars=args.bars,
        formats=args.format
    )

if __name__ == "__main__":
    main()
