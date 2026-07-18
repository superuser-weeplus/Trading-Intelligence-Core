import logging
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger("app.data_collector")

# Try to import MetaTrader5, handle case where it's not installed or running
MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    logger.warning("MetaTrader5 python package not installed. Running in Fallback Mode (Yahoo Finance / Mock Data).")

from app.config import settings
from app.database.connection import LocalSessionLocal
from app.database.models import PriceHistory

class MT5Collector:
    def __init__(self):
        self.connected = False
        self.timeframe_map = {}
        if MT5_AVAILABLE:
            self.timeframe_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
            }

    def connect(self):
        if not MT5_AVAILABLE:
            logger.warning("Cannot connect: MetaTrader5 package is not available.")
            return False
            
        try:
            logger.info("Initializing connection to MetaTrader 5 Terminal...")
            # If path, login, or server is provided in settings, use them
            init_args = {}
            if settings.MT5_PATH:
                init_args["path"] = settings.MT5_PATH
            if settings.MT5_LOGIN:
                init_args["login"] = settings.MT5_LOGIN
                init_args["password"] = settings.MT5_PASSWORD
                init_args["server"] = settings.MT5_SERVER
                
            if not mt5.initialize(**init_args):
                error_code = mt5.last_error()
                logger.error(f"MT5 terminal initialization failed: {error_code}. Running in Fallback Mode.")
                self.connected = False
                return False
            
            logger.info("Successfully connected to MetaTrader 5 Terminal.")
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Error connecting to MT5 terminal: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MetaTrader 5 Terminal.")

    def fetch_historical_data(self, symbol: str, timeframe: str, count: int = 500) -> pd.DataFrame:
        """
        Fetches historical candles. Falls back to yfinance or mock data if MT5 is unavailable.
        """
        # 1. Try MT5
        if MT5_AVAILABLE:
            # Connect if not already connected
            if not self.connected:
                self.connect()
                
            if self.connected:
                # Ensure symbol is active in Market Watch
                mt5.symbol_select(symbol, True)
                
                mt5_tf = self.timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
                logger.info(f"Fetching {count} bars of {symbol} ({timeframe}) from MT5...")
                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)
                
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    # Convert time in seconds to datetime
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df = df.rename(columns={
                        'time': 'timestamp',
                        'tick_volume': 'volume'
                    })
                    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'spread']]
                else:
                    logger.warning(f"Failed to fetch data from MT5 for {symbol}: {mt5.last_error()}. Trying fallback.")

        # 2. Fallback to Yahoo Finance (YFinance)
        return self._fetch_yfinance_fallback(symbol, timeframe, count)

    def _fetch_yfinance_fallback(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        """
        Fallback data downloader using yfinance (useful for stocks and BTC-USD).
        """
        logger.info(f"Using Yahoo Finance fallback for {symbol} ({timeframe})...")
        
        # Map timeframe strings to yfinance intervals
        # yfinance intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        yf_interval_map = {
            "M1": "1m",
            "M5": "5m",
            "M15": "15m",
            "M30": "30m",
            "H1": "1h",
            "H4": "1h", # Approx H1
            "D1": "1d"
        }
        interval = yf_interval_map.get(timeframe, "1d")
        
        # Adjust symbol name if it's forex (e.g. EURUSD -> EURUSD=X)
        yf_symbol = symbol
        if len(symbol) == 6 and symbol.isalpha():
            yf_symbol = f"{symbol}=X" # Yahoo Finance currency pair notation
            
        try:
            import yfinance as yf
            ticker = yf.Ticker(yf_symbol)
            
            # Estimate start date based on count and interval
            # Just download a generous amount and tail it
            period = "1mo"
            if interval == "1d":
                period = "2y"
            elif interval in ["1h", "1m", "5m"]:
                period = "7d"
                
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                df = df.reset_index()
                # yfinance might return 'Date' or 'Datetime'
                time_col = 'Date' if 'Date' in df.columns else 'Datetime'
                df = df.rename(columns={
                    time_col: 'timestamp',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                df['spread'] = 0.0
                df = df.tail(count)
                # Ensure timezone-naive
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'spread']]
        except Exception as e:
            logger.error(f"YFinance fallback failed: {e}. Generating mock data.")
            
        return self._generate_mock_data(symbol, timeframe, count)

    def _generate_mock_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        """
        Creates synthetic price data if all other sources fail.
        """
        logger.info(f"Generating synthetic mock data for {symbol} ({timeframe})...")
        np.random.seed(42)
        
        # Time intervals
        freq_map = {
            "M1": "1min", "M5": "5min", "M15": "15min", 
            "M30": "30min", "H1": "1h", "H4": "4h", "D1": "1D"
        }
        freq = freq_map.get(timeframe, "1h")
        timestamps = pd.date_range(end=datetime.now(), periods=count, freq=freq)
        
        # Random walk
        start_price = 1.1200 if "EUR" in symbol or "USD" in symbol else 100.0
        if "BTC" in symbol:
            start_price = 60000.0
            
        price = start_price
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for _ in range(count):
            change = np.random.normal(0, start_price * 0.001)
            o = price
            c = price + change
            h = max(o, c) + abs(np.random.normal(0, start_price * 0.0005))
            l = min(o, c) - abs(np.random.normal(0, start_price * 0.0005))
            v = float(np.random.randint(100, 5000))
            
            opens.append(o)
            highs.append(h)
            lows.append(l)
            closes.append(c)
            volumes.append(v)
            price = c
            
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes,
            'spread': [1.0] * count
        })
        return df

    def sync_to_db(self, symbol: str, timeframe: str, count: int = 500):
        """
        Fetches data and syncs to SQLite/PostgreSQL, avoiding duplicates.
        """
        df = self.fetch_historical_data(symbol, timeframe, count)
        db = LocalSessionLocal()
        
        new_records = 0
        try:
            for _, row in df.iterrows():
                # Check if timestamp already exists for symbol + timeframe
                exists = db.query(PriceHistory).filter(
                    PriceHistory.symbol == symbol,
                    PriceHistory.timeframe == timeframe,
                    PriceHistory.timestamp == row['timestamp']
                ).first()
                
                if not exists:
                    price_record = PriceHistory(
                        symbol=symbol,
                        timeframe=timeframe,
                        timestamp=row['timestamp'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume']),
                        spread=float(row['spread'])
                    )
                    db.add(price_record)
                    new_records += 1
            db.commit()
            logger.info(f"Sync complete. Added {new_records} new candles for {symbol} ({timeframe}).")
        except Exception as e:
            db.rollback()
            logger.error(f"Error syncing {symbol} data to database: {e}")
        finally:
            db.close()
            
        return new_records
