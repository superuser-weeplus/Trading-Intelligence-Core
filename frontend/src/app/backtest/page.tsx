'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../../components/DashboardLayout';
import { backtestService, alertService, journalService } from '../../services/api';
import { EquityChart } from '../../components/EChart';
import { 
  Play, 
  ArrowUpRight, 
  ArrowDownRight, 
  Settings, 
  PlusCircle, 
  HelpCircle,
  Briefcase
} from 'lucide-react';

export default function BacktestingPage() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState('SMA_Cross');
  const [symbol, setSymbol] = useState('EURUSD');
  const [timeframe, setTimeframe] = useState('H1');
  
  // Params
  const [capital, setCapital] = useState(10000);
  const [commission, setCommission] = useState(0.0001);
  const [stopLoss, setStopLoss] = useState(0.02);
  const [takeProfit, setTakeProfit] = useState(0.04);
  
  // Results
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    backtestService.getStrategies().then((data) => {
      setStrategies(data);
    }).catch(console.error);
  }, []);

  const handleRun = async () => {
    setLoading(true);
    setResults(null);
    try {
      const res = await backtestService.runBacktest({
        symbol,
        timeframe,
        strategy: selectedStrategy,
        initial_capital: capital,
        commission,
        stop_loss_pct: stopLoss,
        take_profit_pct: takeProfit
      });
      setResults(res);
    } catch (e: any) {
      alert(`Backtest failed: ${e.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const importTradesToJournal = async () => {
    if (!results || results.trades.length === 0) return;
    setImporting(true);
    try {
      let imported = 0;
      for (const t of results.trades) {
        // Log trade
        const logged = await journalService.logTrade({
          symbol: t.symbol,
          direction: t.direction,
          size: t.size,
          entry_time: t.entry_time,
          entry_price: t.entry_price,
          notes: `Imported from backtest (${selectedStrategy})`
        });
        
        // Close trade immediately to compute PnL
        await journalService.closeTrade(logged.id!, {
          exit_price: t.exit_price,
          exit_time: t.exit_time,
          notes: t.notes,
          commission: capital * t.size * commission
        });
        imported++;
      }
      alert(`Successfully imported ${imported} trades into your Trading Journal!`);
    } catch (e: any) {
      alert(`Import failed: ${e.message}`);
    } finally {
      setImporting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="border-b border-[#1e1e24] pb-6">
        <h1 className="text-3xl font-bold tracking-tight">Backtesting Lab</h1>
        <p className="text-zinc-400 text-sm">Simulate and evaluate algorithm performances on MetaTrader 5 historical bar data.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left: Configuration form */}
        <div className="card-premium p-6 h-fit space-y-6">
          <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-3">
            <Settings className="h-4 w-4 text-blue-500" />
            <h2 className="text-md font-bold">Configure Simulator</h2>
          </div>

          <div className="space-y-4 text-sm">
            {/* Strategy */}
            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Strategy Type</label>
              <select
                value={selectedStrategy}
                onChange={(e) => setSelectedStrategy(e.target.value)}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none focus:border-blue-500"
              >
                {strategies.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>

            {/* Asset & TF */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Asset</label>
                <select
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                >
                  <option value="XAUUSD">XAUUSD</option>
                  <option value="GBPUSD">GBPUSD</option>
                  <option value="EURUSD">EURUSD</option>
                  <option value="USDJPY">USDJPY</option>
                  <option value="DXY">DXY</option>
                </select>
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Timeframe</label>
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                >
                  <option value="M5">M5</option>
                  <option value="M15">M15</option>
                  <option value="H1">H1</option>
                  <option value="D1">D1</option>
                </select>
              </div>
            </div>

            {/* Capital */}
            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Capital ($)</label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(parseFloat(e.target.value))}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* SL & TP */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Stop Loss (%)</label>
                <input
                  type="number"
                  step="0.005"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(parseFloat(e.target.value))}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                />
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Take Profit (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={takeProfit}
                  onChange={(e) => setTakeProfit(parseFloat(e.target.value))}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                />
              </div>
            </div>

            <button
              onClick={handleRun}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium rounded-lg text-sm transition-all"
            >
              <Play className="h-4 w-4" />
              <span>{loading ? 'Simulating...' : 'Run Simulation'}</span>
            </button>
          </div>
        </div>

        {/* Right: Results displays */}
        <div className="lg:col-span-3 space-y-8">
          {loading ? (
            <div className="h-[400px] flex flex-col items-center justify-center card-premium">
              <div className="animate-spin rounded-full h-10 w-8 border-b-2 border-blue-500 mb-4" />
              <p className="text-zinc-500 text-sm">Evaluating strategy across bars...</p>
            </div>
          ) : results ? (
            <>
              {/* Performance Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="card-premium p-4">
                  <p className="text-zinc-500 text-xs font-semibold uppercase">Net Profit</p>
                  <h4 className={`text-xl font-bold ${results.summary.total_return_pct >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                    {results.summary.total_return_pct.toFixed(2)}%
                  </h4>
                </div>
                <div className="card-premium p-4">
                  <p className="text-zinc-500 text-xs font-semibold uppercase">Sharpe Ratio</p>
                  <h4 className="text-xl font-bold text-zinc-100">{results.summary.sharpe_ratio.toFixed(2)}</h4>
                </div>
                <div className="card-premium p-4">
                  <p className="text-zinc-500 text-xs font-semibold uppercase">Max Drawdown</p>
                  <h4 className="text-xl font-bold text-rose-500">{results.summary.max_drawdown_pct.toFixed(2)}%</h4>
                </div>
                <div className="card-premium p-4">
                  <p className="text-zinc-500 text-xs font-semibold uppercase">Win Rate</p>
                  <h4 className="text-xl font-bold text-zinc-100">{results.summary.win_rate_pct.toFixed(1)}%</h4>
                </div>
              </div>

              {/* Chart */}
              <div className="card-premium p-6">
                <h3 className="font-bold mb-4 text-sm uppercase text-zinc-400">Equity Curve</h3>
                <EquityChart data={results.equity_curve} />
              </div>

              {/* Trade Log */}
              <div className="card-premium p-6">
                <div className="flex items-center justify-between border-b border-[#1e1e24] pb-4 mb-4">
                  <h3 className="font-bold text-zinc-100">Simulation Executed Trades ({results.trades.length})</h3>
                  <button
                    onClick={importTradesToJournal}
                    disabled={importing || results.trades.length === 0}
                    className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600/10 text-emerald-500 border border-emerald-500/20 rounded-md text-xs font-semibold hover:bg-emerald-600/20 transition-all disabled:opacity-50"
                  >
                    <Briefcase className="h-3.5 w-3.5" />
                    <span>Import to Journal</span>
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-zinc-400 border-collapse">
                    <thead>
                      <tr className="border-b border-[#1e1e24] text-zinc-500 uppercase tracking-wider font-semibold">
                        <th className="py-2.5">Asset</th>
                        <th className="py-2.5">Type</th>
                        <th className="py-2.5">Entry Price</th>
                        <th className="py-2.5">Exit Price</th>
                        <th className="py-2.5">Entry Time</th>
                        <th className="py-2.5">Exit Time</th>
                        <th className="py-2.5 text-right">Net P&L</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1e1e24]/60">
                      {results.trades.map((t: any, idx: number) => (
                        <tr key={idx} className="hover:bg-zinc-800/10">
                          <td className="py-3 font-semibold text-zinc-200">{t.symbol}</td>
                          <td className="py-3">
                            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                              t.direction === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                            }`}>{t.direction}</span>
                          </td>
                          <td className="py-3">${t.entry_price.toFixed(4)}</td>
                          <td className="py-3">${t.exit_price.toFixed(4)}</td>
                          <td className="py-3 text-zinc-500">{t.entry_time}</td>
                          <td className="py-3 text-zinc-500">{t.exit_time}</td>
                          <td className={`py-3 text-right font-bold ${t.pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {t.pnl >= 0 ? '+' : ''}${t.pnl.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="h-[400px] flex flex-col items-center justify-center card-premium text-zinc-500 space-y-4">
              <Briefcase className="h-12 w-12 text-zinc-700" />
              <div className="text-center">
                <h3 className="font-semibold text-zinc-300">No Simulation Data</h3>
                <p className="text-xs max-w-sm mt-1">Configure the strategy and metrics on the left pane and hit Run Simulation.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
