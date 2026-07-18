import logging
import pandas as pd
import numpy as np
from datetime import datetime
from app.database.connection import LocalSessionLocal
from app.database.models import PriceHistory
from app.indicator_engine.indicators import TechnicalIndicators

logger = logging.getLogger("app.backtesting.engine")

class BacktestEngine:
    @staticmethod
    def run_backtest(symbol: str, timeframe: str, strategy: str, initial_capital: float = 10000.0, commission: float = 0.0001, stop_loss_pct: float = 0.02, take_profit_pct: float = 0.04) -> dict:
        """
        Runs a historical simulation of a strategy on stored price data.
        """
        logger.info(f"Running backtest for {symbol} ({timeframe}) using strategy '{strategy}'...")
        db = LocalSessionLocal()
        
        try:
            # 1. Fetch data
            query = db.query(PriceHistory).filter(
                PriceHistory.symbol == symbol,
                PriceHistory.timeframe == timeframe
            ).order_by(PriceHistory.timestamp.asc())
            
            prices_count = query.count()
            if prices_count < 100:
                return {"error": f"Insufficient historical data in DB: {prices_count} bars. Sync data first."}
                
            df = pd.DataFrame([{
                "timestamp": p.timestamp,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume
            } for p in query.all()])
            
            # 2. Add indicators
            df = TechnicalIndicators.apply_all(df)
            
            # 3. Generate Strategy Signals
            # Signals: 1 = BUY, -1 = SELL, 0 = HOLD/EXIT
            try:
                from app.strategies import StrategyRegistry
                strategy_instance = StrategyRegistry.get_strategy(strategy)
                df["signal"] = strategy_instance.generate_signals(df, strategy_instance.default_parameters)
            except Exception as e:
                logger.error(f"Error executing strategy '{strategy}': {e}")
                # Fallback to Buy & Hold
                df["signal"] = 0
                df.loc[0, "signal"] = 1
            
            # 4. Run Event Simulation
            capital = initial_capital
            position = 0.0  # Current units of asset held
            trades = []
            equity_curve = []
            
            # Track state
            in_position = False
            entry_price = 0.0
            entry_time = None
            entry_fee = 0.0
            
            for idx, row in df.iterrows():
                current_price = row["close"]
                current_time = row["timestamp"]
                
                # Check Stop Loss / Take Profit if in position
                if in_position:
                    pnl_pct = (current_price - entry_price) / entry_price if position > 0 else (entry_price - current_price) / entry_price
                    
                    # Triggers
                    is_stop_loss = pnl_pct <= -stop_loss_pct
                    is_take_profit = pnl_pct >= take_profit_pct
                    
                    if is_stop_loss or is_take_profit:
                        # Close position
                        exit_price = current_price
                        trade_pnl = position * (exit_price - entry_price)
                        exit_fee = exit_price * abs(position) * commission
                        pnl_net = trade_pnl - entry_fee - exit_fee
                        capital += pnl_net + (position * entry_price) # refund entry value + net pnl
                        
                        trades.append({
                            "symbol": symbol,
                            "direction": "BUY" if position > 0 else "SELL",
                            "size": abs(position),
                            "entry_time": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "exit_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "pnl": pnl_net,
                            "notes": f"Exit via {'Stop Loss' if is_stop_loss else 'Take Profit'}"
                        })
                        
                        position = 0.0
                        in_position = False
                
                # Evaluate new signals
                signal = row["signal"]
                if signal == 1 and not in_position: # BUY Signal
                    entry_price = current_price
                    entry_time = current_time
                    # Risk 10% of capital per trade
                    trade_capital = capital * 0.1
                    position = trade_capital / entry_price
                    capital -= trade_capital
                    entry_fee = trade_capital * commission
                    in_position = True
                    
                elif signal == -1 and in_position: # EXIT/SELL Signal
                    exit_price = current_price
                    trade_pnl = position * (exit_price - entry_price)
                    exit_fee = exit_price * abs(position) * commission
                    pnl_net = trade_pnl - entry_fee - exit_fee
                    capital += pnl_net + (position * entry_price)
                    
                    trades.append({
                        "symbol": symbol,
                        "direction": "BUY",
                        "size": abs(position),
                        "entry_time": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "exit_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl": pnl_net,
                        "notes": "Exit via strategy signal"
                    })
                    
                    position = 0.0
                    in_position = False
                    
                # Track equity (cash + current value of position)
                current_value = position * current_price if in_position else 0.0
                total_equity = capital + current_value
                equity_curve.append({
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "equity": total_equity
                })
            
            # Close any open positions at the end of backtest
            if in_position:
                exit_price = df.iloc[-1]["close"]
                current_time = df.iloc[-1]["timestamp"]
                trade_pnl = position * (exit_price - entry_price)
                exit_fee = exit_price * abs(position) * commission
                pnl_net = trade_pnl - entry_fee - exit_fee
                capital += pnl_net + (position * entry_price)
                
                trades.append({
                    "symbol": symbol,
                    "direction": "BUY",
                    "size": abs(position),
                    "entry_time": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "exit_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": pnl_net,
                    "notes": "Close at end of backtest"
                })
                
                equity_curve[-1]["equity"] = capital

            # 5. Compute performance statistics
            pnl_list = [t["pnl"] for t in trades]
            total_trades = len(trades)
            
            win_trades = [p for p in pnl_list if p > 0]
            loss_trades = [p for p in pnl_list if p <= 0]
            win_rate = len(win_trades) / total_trades if total_trades > 0 else 0.0
            
            sum_gains = sum(win_trades)
            sum_losses = abs(sum(loss_trades))
            profit_factor = sum_gains / sum_losses if sum_losses > 0 else (sum_gains if sum_gains > 0 else 1.0)
            
            # Buy & Hold Return
            bh_return = ((df.iloc[-1]["close"] - df.iloc[0]["close"]) / df.iloc[0]["close"]) * 100.0
            
            # System Return
            system_return = ((capital - initial_capital) / initial_capital) * 100.0
            
            # Drawdown and Sharpe Ratio calculation
            equity_series = pd.Series([eq["equity"] for eq in equity_curve])
            equity_returns = equity_series.pct_change().dropna()
            
            # Annualized Sharpe (assuming daily returns, 252 trading days. If M15/H1, standard Sharpe is scaled differently, but we approximate daily scale)
            avg_return = equity_returns.mean()
            std_return = equity_returns.std()
            sharpe = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0.0
            
            # Max Drawdown
            rolling_max = equity_series.cummax()
            drawdowns = (equity_series - rolling_max) / rolling_max
            max_drawdown = drawdowns.min() * 100.0 # as negative percentage
            
            return {
                "summary": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "strategy": strategy,
                    "initial_capital": initial_capital,
                    "final_capital": capital,
                    "total_return_pct": system_return,
                    "buy_and_hold_pct": bh_return,
                    "sharpe_ratio": float(sharpe),
                    "max_drawdown_pct": float(max_drawdown),
                    "total_trades": total_trades,
                    "win_rate_pct": win_rate * 100.0,
                    "profit_factor": float(profit_factor)
                },
                "trades": trades,
                "equity_curve": equity_curve
            }
            
        except Exception as e:
            logger.error(f"Error executing backtest: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"error": f"Error executing backtest: {e}"}
        finally:
            db.close()
