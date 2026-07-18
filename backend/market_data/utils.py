import os
import pandas as pd
import logging
from typing import List

logger = logging.getLogger("market_data_exporter.utils")

def ensure_directory(path: str) -> str:
    """
    Ensures directory path exists, creating it recursively if needed.
    """
    os.makedirs(path, exist_ok=True)
    return path

def format_rates_dataframe(rates_data) -> pd.DataFrame:
    """
    Formats raw MT5 rates or dictionary list into standard OHLCV DataFrame.
    """
    if rates_data is None or len(rates_data) == 0:
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'spread'])

    df = pd.DataFrame(rates_data)
    
    # Standardize timestamp
    if 'time' in df.columns:
        if pd.api.types.is_numeric_dtype(df['time']):
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        else:
            df['timestamp'] = pd.to_datetime(df['time'])
    elif 'timestamp' not in df.columns:
        df['timestamp'] = pd.to_datetime(df.index)

    # Standardize volume
    if 'tick_volume' in df.columns:
        df['volume'] = df['tick_volume']
    elif 'Volume' in df.columns:
        df['volume'] = df['Volume']
    elif 'volume' not in df.columns:
        df['volume'] = 0.0

    # Ensure required columns lowercase
    column_mapping = {
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Spread': 'spread'
    }
    df = df.rename(columns=column_mapping)
    
    if 'spread' not in df.columns:
        df['spread'] = 0.0

    # Required columns order
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'spread']
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0

    # Sort chronological
    df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
    return df[required_cols]

def save_export_file(df: pd.DataFrame, file_path_without_ext: str, export_format: str) -> str:
    """
    Saves DataFrame to specified format (csv, json, parquet). Returns generated filepath.
    """
    export_format = export_format.lower().strip()
    target_file = f"{file_path_without_ext}.{export_format}"
    
    try:
        if export_format == "csv":
            df.to_csv(target_file, index=False)
        elif export_format == "json":
            # Format datetime ISO string
            df_json = df.copy()
            df_json['timestamp'] = df_json['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            df_json.to_json(target_file, orient='records', indent=2)
        elif export_format == "parquet":
            try:
                df.to_parquet(target_file, index=False)
            except Exception as pe:
                logger.error(f"Failed to export Parquet format (pyarrow/fastparquet required): {pe}")
                raise pe
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
            
        logger.info(f"Successfully exported {len(df)} rows to: {target_file}")
        return target_file
    except Exception as e:
        logger.error(f"Error saving file '{target_file}': {e}")
        raise e

import json
from datetime import datetime

def write_symbol_metadata(symbol: str, broker_symbol: str, symbol_dir: str, results: List[Any]) -> str:
    """
    Generates and writes metadata.json for a specific symbol directory.
    """
    meta_path = os.path.join(symbol_dir, "metadata.json")
    
    existing_timeframes = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                existing_timeframes = old_data.get("timeframes", {})
        except Exception:
            pass

    timeframes_meta = existing_timeframes.copy()
    
    for r in results:
        if r.symbol.upper() == symbol.upper() and r.success:
            timeframes_meta[r.timeframe] = {
                "bars": r.bars_fetched,
                "start_time": r.start_time,
                "end_time": r.end_time,
                "files": [os.path.basename(f) for f in r.saved_files]
            }

    metadata = {
        "symbol": symbol.upper(),
        "broker_symbol": broker_symbol,
        "last_updated": datetime.now().isoformat(),
        "columns": ["timestamp", "open", "high", "low", "close", "volume", "spread"],
        "timeframes": timeframes_meta
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    logger.info(f"Generated symbol metadata: {meta_path}")
    return meta_path

def write_manifest(output_dir: str, results: List[Any]) -> str:
    """
    Generates and writes manifest.json at the root output directory.
    """
    manifest_path = os.path.join(output_dir, "manifest.json")
    
    symbols_map = {}
    for r in results:
        sym = r.symbol.upper()
        if sym not in symbols_map:
            symbols_map[sym] = []
        symbols_map[sym].append(r)

    datasets = []
    for sym, res_list in symbols_map.items():
        timeframes = [r.timeframe for r in res_list if r.success]
        total_bars = sum(r.bars_fetched for r in res_list if r.success)
        datasets.append({
            "symbol": sym,
            "metadata_file": f"{sym}/metadata.json",
            "timeframes_available": timeframes,
            "total_bars": total_bars,
            "status": "active"
        })

    manifest = {
        "generator": "Trading Intelligence Core MT5 Market Data Exporter",
        "version": "1.1",
        "generated_at": datetime.now().isoformat(),
        "total_symbols": len(datasets),
        "exported_symbols": list(symbols_map.keys()),
        "datasets": datasets
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Generated global manifest catalog: {manifest_path}")
    return manifest_path
