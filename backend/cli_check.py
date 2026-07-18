import os
import sys
import logging
from datetime import datetime

# Ensure backend folder is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import local_engine, LocalBase, LocalSessionLocal
from app.database.models import PriceHistory
from app.data_collector.collector import MT5Collector
from app.indicator_engine.indicators import TechnicalIndicators
from app.ai_engine.models import MLEngine
from app.ai_engine.llm_helper import LLMHelper

# Suppress logs for a clean CLI output
logging.getLogger("app.database").setLevel(logging.WARNING)
logging.getLogger("app.data_collector").setLevel(logging.WARNING)
logging.getLogger("app.ai_engine.models").setLevel(logging.WARNING)
logging.getLogger("app.ai_engine.llm_helper").setLevel(logging.WARNING)

# Symbol mapping (Exness cent account symbols vs Standard symbols)
SYMBOL_MAPPING = {
    "XAUUSD": "XAUUSDc",
    "GBPUSD": "GBPUSDc",
    "EURUSD": "EURUSDc",
    "USDJPY": "USDJPYc",
    "DXY": "DX-Y.NYB" # US Dollar Index on Yahoo Finance
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    print("=" * 60)
    print(f" {title.center(58)} ")
    print("=" * 60)

def main_menu():
    collector = MT5Collector()
    llm_helper = LLMHelper()
    
    # Initialize SQLite tables
    LocalBase.metadata.create_all(bind=local_engine)
    
    while True:
        clear_screen()
        print_header("Trading Intelligence CLI Check Console")
        print("Select a symbol to sync and check latest data:")
        print(" 1. XAUUSD (Gold - MT5)")
        print(" 2. GBPUSD (Pound / Dollar - MT5)")
        print(" 3. EURUSD (Euro / Dollar - MT5)")
        print(" 4. USDJPY (Dollar / Yen - MT5)")
        print(" 5. DXY (US Dollar Index - Yahoo Finance)")
        print(" 6. Exit")
        print("-" * 60)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '6':
            print("\nExiting CLI Check Console. Goodbye!")
            break
            
        choices = {
            '1': "XAUUSD",
            '2': "GBPUSD",
            '3': "EURUSD",
            '4': "USDJPY",
            '5': "DXY"
        }
        
        if choice not in choices:
            input("\nInvalid choice. Press Enter to try again...")
            continue
            
        symbol = choices[choice]
        mt5_symbol = SYMBOL_MAPPING[symbol]
        
        print(f"\n[+] Selected: {symbol} (Target MT5/YFinance Symbol: {mt5_symbol})")
        print("[+] Syncing latest 100 bars (H1 timeframe) from source...")
        
        try:
            # Sync to local DB
            new_records = collector.sync_to_db(mt5_symbol, "H1", 100)
            
            # Fetch prices from Local DB
            db = LocalSessionLocal()
            prices = db.query(PriceHistory).filter(
                PriceHistory.symbol == mt5_symbol,
                PriceHistory.timeframe == "H1"
            ).order_by(PriceHistory.timestamp.asc()).all()
            
            if not prices:
                print("[-] Error: No price history could be fetched or generated.")
                db.close()
                input("\nPress Enter to return to main menu...")
                continue
                
            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame([{
                "timestamp": p.timestamp,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume
            } for p in prices])
            
            db.close()
            
            # Calculate Indicators
            df_ind = TechnicalIndicators.apply_all(df)
            latest_row = df_ind.tail(1).iloc[0]
            
            # Run ML Prediction
            prediction = MLEngine.predict_latest(mt5_symbol, "H1", df)
            
            # Generate LLM Rationale
            indicators_dict = {
                "close": latest_row["close"],
                "rsi_14": latest_row["rsi_14"],
                "macd_hist": latest_row["macd_hist"],
                "bb_percent": latest_row["bb_percent"],
                "atr_14": latest_row["atr_14"]
            }
            rationale = llm_helper.generate_market_rationale(mt5_symbol, "H1", indicators_dict, prediction)
            
            # Print Details
            clear_screen()
            print_header(f"MARKET METRICS CARD: {symbol}")
            print(f"Timeframe: H1 | Local Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Candle Time: {latest_row['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print("-" * 60)
            
            # OHLCV
            print(f"Open:  {latest_row['open']:.5f}  |  High: {latest_row['high']:.5f}")
            print(f"Low:   {latest_row['low']:.5f}  |  Close: {latest_row['close']:.5f}")
            print(f"Volume: {latest_row['volume']:.1f}")
            print("-" * 60)
            
            # Technical Indicators
            print("Technical Indicators:")
            print(f" - RSI (14):     {latest_row['rsi_14']:.2f}")
            print(f" - MACD Hist:    {latest_row['macd_hist']:.6f}")
            print(f" - BB Bands:     [{latest_row['bb_lower']:.5f} - {latest_row['bb_upper']:.5f}]")
            print(f" - BB Percent:   {latest_row['bb_percent']:.2f} (0=Lower, 1=Upper)")
            print(f" - ATR (14):     {latest_row['atr_14']:.5f}")
            print("-" * 60)
            
            # AI ML / LLM
            print("AI & Machine Learning Signals:")
            direction_color = "\033[92m" if prediction['direction'] == 'UP' else "\033[91m" if prediction['direction'] == 'DOWN' else "\033[0m"
            reset_color = "\033[0m"
            print(f" - ML Prediction: {direction_color}{prediction['direction']}{reset_color}")
            print(f" - Probability:   {prediction['probability']*100:.1f}% UP")
            print(f" - Confidence:    {prediction['confidence']*100:.1f}%")
            print("-" * 60)
            
            print("AI Advisor Analysis:")
            print(f" {rationale}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n[-] Error running metrics check: {e}")
            import traceback
            traceback.print_exc()
            
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting CLI Check Console. Goodbye!")
