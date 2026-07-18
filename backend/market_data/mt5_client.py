import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

logger = logging.getLogger("market_data_exporter.mt5_client")

# Try to import MetaTrader5
MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    logger.warning("MetaTrader5 python package not installed. Running in Fallback Mode.")

class MT5Client:
    """
    MT5 API Client wrapper with fallback support for data collection.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.connected = False
        self.timeframe_map = {}
        
        if MT5_AVAILABLE:
            self.timeframe_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M2": mt5.TIMEFRAME_M2,
                "M3": mt5.TIMEFRAME_M3,
                "M4": mt5.TIMEFRAME_M4,
                "M5": mt5.TIMEFRAME_M5,
                "M6": mt5.TIMEFRAME_M6,
                "M10": mt5.TIMEFRAME_M10,
                "M12": mt5.TIMEFRAME_M12,
                "M15": mt5.TIMEFRAME_M15,
                "M20": mt5.TIMEFRAME_M20,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H2": mt5.TIMEFRAME_H2,
                "H3": mt5.TIMEFRAME_H3,
                "H4": mt5.TIMEFRAME_H4,
                "H6": mt5.TIMEFRAME_H6,
                "H8": mt5.TIMEFRAME_H8,
                "H12": mt5.TIMEFRAME_H12,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
                "MN1": mt5.TIMEFRAME_MN1,
            }

    def connect(self) -> bool:
        """
        Initializes connection to MetaTrader 5 terminal.
        """
        if not MT5_AVAILABLE:
            logger.warning("MetaTrader5 package is not available. Using fallback mode.")
            self.connected = False
            return False

        try:
            init_args = {}
            path = self.config.get("path")
            login = self.config.get("login")
            password = self.config.get("password")
            server = self.config.get("server")

            if path:
                init_args["path"] = path
            if login:
                init_args["login"] = int(login)
            if password:
                init_args["password"] = str(password)
            if server:
                init_args["server"] = str(server)

            logger.info("Initializing connection to MetaTrader 5 Terminal...")
            if not mt5.initialize(**init_args):
                err = mt5.last_error()
                logger.warning(f"MT5 initialization failed: {err}. Entering Fallback Mode.")
                self.connected = False
                return False

            self.connected = True
            terminal_info = mt5.terminal_info()
            if terminal_info:
                logger.info(f"Connected to MT5 Terminal: {terminal_info.name} ({terminal_info.company})")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MT5 terminal: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """
        Closes connection to MetaTrader 5.
        """
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MetaTrader 5 Terminal.")

    def fetch_rates(self, symbol: str, timeframe: str, count: int = 5000) -> pd.DataFrame:
        """
        Fetches historical price bars for the given symbol and timeframe.
        """
        if not self.connected:
            self.connect()

        if self.connected:
            try:
                # Ensure symbol is active in MarketWatch
                mt5.symbol_select(symbol, True)
                
                mt5_tf = self.timeframe_map.get(timeframe.upper())
                if mt5_tf is None:
                    logger.error(f"Invalid timeframe: {timeframe}")
                    return pd.DataFrame()

                logger.info(f"Fetching {count} bars for {symbol} ({timeframe}) from MT5...")
                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)

                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    return df
                else:
                    err = mt5.last_error()
                    logger.warning(f"No rates returned from MT5 for {symbol} ({timeframe}): {err}. Using Fallback.")
            except Exception as e:
                logger.error(f"MT5 fetch exception for {symbol}: {e}")

        # Fallback if MT5 fetch failed or not connected
        return self._fetch_fallback(symbol, timeframe, count)

    def _fetch_fallback(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        """
        Fallback data generator using yfinance or synthetic data generator.
        """
        tf_upper = timeframe.upper()
        logger.info(f"Fetching fallback data for {symbol} ({tf_upper})...")
        
        # Map timeframe to yfinance interval
        # yfinance intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        # Multi-hour timeframes (H2-H12) download 1h and resample to target timeframe.
        yf_map = {
            "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
            "H1": "1h", "H2": "1h", "H3": "1h", "H4": "1h", "H6": "1h", "H8": "1h", "H12": "1h",
            "D1": "1d", "W1": "1wk"
        }
        interval = yf_map.get(tf_upper, "1h")
        
        # Clean symbol for yfinance
        yf_symbol = symbol.replace("c", "")  # strip broker cent suffix if present
        if len(yf_symbol) == 6 and yf_symbol.isalpha():
            yf_symbol = f"{yf_symbol}=X"
        elif yf_symbol == "DXY" or yf_symbol == "DX-Y.NYB":
            yf_symbol = "DX-Y.NYB"

        try:
            import yfinance as yf
            logger.info(f"Downloading from Yahoo Finance for {yf_symbol} (interval={interval})...")
            if interval in ["1d", "1wk"]:
                period = "max"
            elif interval in ["1h"]:
                period = "730d"
            else:
                period = "60d"

            df = yf.Ticker(yf_symbol).history(period=period, interval=interval)
            
            if not df.empty:
                df = df.reset_index()
                time_col = 'Date' if 'Date' in df.columns else 'Datetime'
                df = df.rename(columns={
                    time_col: 'time',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'tick_volume'
                })
                df['spread'] = 0.0
                df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)

                # Resample 1h candles to multi-hour timeframes (H2, H3, H4, H6, H8, H12)
                if tf_upper in ["H2", "H3", "H4", "H6", "H8", "H12"]:
                    hours = tf_upper.replace("H", "")
                    freq_rule = f"{hours}h"
                    logger.info(f"Resampling 1h data into {freq_rule} OHLCV candles...")
                    df = df.set_index('time').resample(freq_rule).agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                        'tick_volume': 'sum',
                        'spread': 'mean'
                    }).dropna().reset_index()

                return df.tail(count)
        except Exception as e:
            logger.warning(f"Yahoo Finance fallback failed: {e}. Generating synthetic dataset.")

        # Synthetic fallback
        return self._generate_synthetic_data(symbol, timeframe, count)

    def _generate_synthetic_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        """
        Generates realistic synthetic OHLCV bars when external sources are offline.
        """
        logger.info(f"Generating {count} synthetic bars for {symbol} ({timeframe})...")
        np.random.seed(42)
        
        freq_map = {
            "M1": "1min", "M5": "5min", "M15": "15min", "M30": "30min",
            "H1": "1h", "H4": "4h", "D1": "1D"
        }
        freq = freq_map.get(timeframe.upper(), "1h")
        timestamps = pd.date_range(end=datetime.now(), periods=count, freq=freq)
        
        base_price = 2000.0 if "XAU" in symbol else (1.1000 if "EUR" in symbol or "GBP" in symbol else 100.0)
        price = base_price
        
        opens, highs, lows, closes, volumes = [], [], [], [], []
        for _ in range(count):
            change = np.random.normal(0, base_price * 0.001)
            o = price
            c = price + change
            h = max(o, c) + abs(np.random.normal(0, base_price * 0.0005))
            l = min(o, c) - abs(np.random.normal(0, base_price * 0.0005))
            v = float(np.random.randint(500, 10000))
            
            opens.append(o)
            highs.append(h)
            lows.append(l)
            closes.append(c)
            volumes.append(v)
            price = c

        return pd.DataFrame({
            'time': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'tick_volume': volumes,
            'spread': [1.0] * count
        })
