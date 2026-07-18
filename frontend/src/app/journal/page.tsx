'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../../components/DashboardLayout';
import { journalService, Trade } from '../../services/api';
import { WinLossChart } from '../../components/EChart';
import { 
  BookOpen, 
  PlusCircle, 
  XCircle, 
  Check, 
  TrendingUp,
  BrainCircuit,
  Tag
} from 'lucide-react';

export default function JournalPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [stats, setStats] = useState<any>({
    total_trades: 0,
    win_rate_pct: 0.0,
    profit_factor: 1.0,
    total_pnl: 0.0,
    avg_gain: 0.0,
    avg_loss: 0.0,
    max_win: 0.0,
    max_loss: 0.0
  });

  // Log Trade Form
  const [symbol, setSymbol] = useState('EURUSD');
  const [direction, setDirection] = useState<'BUY' | 'SELL'>('BUY');
  const [size, setSize] = useState(0.1);
  const [price, setPrice] = useState(1.1200);
  const [notes, setNotes] = useState('');
  const [emotionalState, setEmotionalState] = useState('disciplined');
  const [tags, setTags] = useState('');
  
  // Close Trade modal
  const [closeTradeId, setCloseTradeId] = useState<number | null>(null);
  const [exitPrice, setExitPrice] = useState(0);
  const [closeNotes, setCloseNotes] = useState('');

  const loadJournal = async () => {
    try {
      const data = await journalService.getTrades();
      setTrades(data);
      const st = await journalService.getStats();
      setStats(st);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadJournal();
  }, []);

  const handleAddTrade = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await journalService.logTrade({
        symbol,
        direction,
        size,
        entry_price: price,
        entry_time: new Date().toISOString(),
        notes,
        emotional_state: emotionalState,
        tags
      });
      alert('Trade entry logged successfully.');
      setNotes('');
      setTags('');
      loadJournal();
    } catch (err: any) {
      alert(`Failed: ${err.message}`);
    }
  };

  const handleCloseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!closeTradeId) return;
    try {
      await journalService.closeTrade(closeTradeId, {
        exit_price: exitPrice,
        exit_time: new Date().toISOString(),
        notes: closeNotes
      });
      setCloseTradeId(null);
      setCloseNotes('');
      loadJournal();
    } catch (err: any) {
      alert(`Failed to close trade: ${err.message}`);
    }
  };

  const openCloseModal = (trade: Trade) => {
    setCloseTradeId(trade.id!);
    setExitPrice(trade.entry_price);
  };

  const wins = trades.filter(t => t.status === 'CLOSED' && (t.pnl ?? 0) > 0).length;
  const losses = trades.filter(t => t.status === 'CLOSED' && (t.pnl ?? 0) <= 0).length;

  return (
    <DashboardLayout>
      <div className="border-b border-[#1e1e24] pb-6">
        <h1 className="text-3xl font-bold tracking-tight">Trading Journal</h1>
        <p className="text-zinc-400 text-sm font-light">Log trades, analyze stats, and evaluate psychological patterns.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: P&L */}
          <div className="card-premium p-6 flex flex-col justify-between">
            <span className="text-xs text-zinc-500 uppercase font-semibold">Accumulated Returns</span>
            <h3 className={`text-3xl font-black mt-4 ${(stats?.total_pnl ?? 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
              {(stats?.total_pnl ?? 0) >= 0 ? '+' : ''}${(stats?.total_pnl ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-zinc-400 mt-2">Win rate: {(stats.win_rate_pct ?? 0.0).toFixed(1)}%</p>
          </div>

          {/* Card 2: Average Gains */}
          <div className="card-premium p-6 flex flex-col justify-between">
            <span className="text-xs text-zinc-500 uppercase font-semibold">Average Gain / Loss</span>
            <div className="mt-4 space-y-1">
              <p className="text-emerald-500 font-semibold text-lg">Avg Gain: +${(stats.avg_gain ?? 0.0).toFixed(2)}</p>
              <p className="text-rose-500 font-semibold text-lg">Avg Loss: -${Math.abs(stats.avg_loss ?? 0.0).toFixed(2)}</p>
            </div>
            <p className="text-xs text-zinc-400 mt-2">Profit Factor: {(stats.profit_factor ?? 1.0).toFixed(2)}</p>
          </div>

          {/* Card 3: Extr. Trades */}
          <div className="card-premium p-6 flex flex-col justify-between">
            <span className="text-xs text-zinc-500 uppercase font-semibold">Outliers (Max Win/Loss)</span>
            <div className="mt-4 space-y-1">
              <p className="text-emerald-500 text-sm font-semibold">Max Win: +${(stats.max_win ?? 0.0).toFixed(2)}</p>
              <p className="text-rose-500 text-sm font-semibold">Max Loss: -${Math.abs(stats.max_loss ?? 0.0).toFixed(2)}</p>
            </div>
            <p className="text-xs text-zinc-400 mt-2">Total Closed Trades: {stats.total_trades ?? 0}</p>
          </div>
        </div>

        {/* Win/Loss Pie chart card */}
        <div className="card-premium p-6 flex flex-col justify-between items-center">
          <span className="text-xs text-zinc-500 uppercase font-semibold text-left w-full border-b border-[#1e1e24] pb-2">Ratio</span>
          <WinLossChart wins={wins} losses={losses} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Log new trade */}
        <div className="card-premium p-6 space-y-6">
          <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-3">
            <PlusCircle className="h-4 w-4 text-blue-500" />
            <h2 className="text-md font-bold">Log New Position</h2>
          </div>

          <form onSubmit={handleAddTrade} className="space-y-4 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Symbol</label>
                <select
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none"
                >
                  <option value="XAUUSD">XAUUSD</option>
                  <option value="GBPUSD">GBPUSD</option>
                  <option value="EURUSD">EURUSD</option>
                  <option value="USDJPY">USDJPY</option>
                  <option value="DXY">DXY</option>
                </select>
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Direction</label>
                <select
                  value={direction}
                  onChange={(e) => setDirection(e.target.value as any)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Size (Lots)</label>
                <input
                  type="number"
                  step="0.01"
                  value={size}
                  onChange={(e) => setSize(parseFloat(e.target.value))}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                />
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Entry Price</label>
                <input
                  type="number"
                  step="0.0001"
                  value={price}
                  onChange={(e) => setPrice(parseFloat(e.target.value))}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm"
                />
              </div>
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Emotional State</label>
              <select
                value={emotionalState}
                onChange={(e) => setEmotionalState(e.target.value)}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none"
              >
                <option value="disciplined">Disciplined / Balanced</option>
                <option value="FOMO">FOMO / Greedy</option>
                <option value="scared">Anxious / Scared</option>
                <option value="frustrated">Frustrated / Revenge trade</option>
              </select>
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Tags</label>
              <input
                type="text"
                placeholder="trend, support, breakout"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none"
              />
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 text-sm focus:outline-none h-16"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg text-sm transition-all"
            >
              Log Entry
            </button>
          </form>
        </div>

        {/* Right: Listed trade history */}
        <div className="lg:col-span-2 space-y-6">
          {/* Close Trade Modal overlay if ID set */}
          {closeTradeId !== null && (
            <div className="card-premium p-6 border border-emerald-500/30 bg-[#0c0c0f] space-y-4">
              <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-2 text-emerald-500">
                <Check className="h-5 w-5" />
                <h3 className="font-bold">Close Active Position</h3>
              </div>
              <form onSubmit={handleCloseSubmit} className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col space-y-1.5">
                    <label className="text-xs font-semibold text-zinc-500 uppercase">Exit Price</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={exitPrice}
                      onChange={(e) => setExitPrice(parseFloat(e.target.value))}
                      className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100"
                    />
                  </div>
                  <div className="flex flex-col space-y-1.5 justify-end">
                    <button
                      type="submit"
                      className="py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-sm transition-all"
                    >
                      Confirm Exit
                    </button>
                  </div>
                </div>
                <div className="flex flex-col space-y-1.5">
                  <label className="text-xs font-semibold text-zinc-500 uppercase">Closing notes</label>
                  <input
                    type="text"
                    value={closeNotes}
                    onChange={(e) => setCloseNotes(e.target.value)}
                    className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100"
                  />
                </div>
              </form>
            </div>
          )}

          <div className="card-premium p-6">
            <h3 className="font-bold text-zinc-100 border-b border-[#1e1e24] pb-4 mb-4">Trade Log History</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-zinc-400 border-collapse">
                <thead>
                  <tr className="border-b border-[#1e1e24] text-zinc-500 uppercase tracking-wider font-semibold">
                    <th className="py-2.5">Asset</th>
                    <th className="py-2.5">Direction</th>
                    <th className="py-2.5">Lots</th>
                    <th className="py-2.5">Entry Price</th>
                    <th className="py-2.5">Exit Price</th>
                    <th className="py-2.5">Tags/Psychology</th>
                    <th className="py-2.5">Status</th>
                    <th className="py-2.5 text-right">PnL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e1e24]/60">
                  {trades.map((t) => (
                    <tr key={t.id} className="hover:bg-zinc-800/10">
                      <td className="py-3 font-semibold text-zinc-200">{t.symbol}</td>
                      <td className="py-3">
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                          t.direction === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'
                        }`}>{t.direction}</span>
                      </td>
                      <td className="py-3 font-mono">{t.size}</td>
                      <td className="py-3 font-mono">${t.entry_price.toFixed(4)}</td>
                      <td className="py-3 font-mono">${t.exit_price ? t.exit_price.toFixed(4) : '-'}</td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-1">
                          {t.emotional_state && (
                            <span className="text-[10px] bg-blue-900/10 text-blue-400 border border-blue-900/20 px-1 py-0.5 rounded flex items-center space-x-0.5">
                              <BrainCircuit className="h-2.5 w-2.5" />
                              <span>{t.emotional_state}</span>
                            </span>
                          )}
                          {t.tags && t.tags.split(',').map((tag, idx) => (
                            <span key={idx} className="text-[10px] bg-zinc-800 text-zinc-400 px-1 py-0.5 rounded flex items-center space-x-0.5">
                              <Tag className="h-2 w-2" />
                              <span>{tag.trim()}</span>
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3">
                        {t.status === 'OPEN' ? (
                          <button
                            onClick={() => openCloseModal(t)}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold px-2 py-0.5 rounded flex items-center space-x-1"
                          >
                            <span>OPEN</span>
                          </button>
                        ) : (
                          <span className="text-zinc-500 text-[10px] font-semibold bg-zinc-800/80 px-2 py-0.5 rounded">CLOSED</span>
                        )}
                      </td>
                      <td className={`py-3 text-right font-bold ${t.pnl && t.pnl >= 0 ? 'text-emerald-500' : t.pnl ? 'text-rose-500' : 'text-zinc-500'}`}>
                        {t.status === 'CLOSED' ? (t.pnl! >= 0 ? '+' : '') + `$${t.pnl!.toFixed(2)}` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
