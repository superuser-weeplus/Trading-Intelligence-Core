'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../../components/DashboardLayout';
import { TVChart } from '../../components/TVChart';
import { marketService, aiService, PriceBar } from '../../services/api';
import { 
  Cpu, 
  RefreshCw, 
  AlertCircle,
  HelpCircle,
  Activity
} from 'lucide-react';

export default function ChartPage() {
  const [symbol, setSymbol] = useState('EURUSD');
  const [timeframe, setTimeframe] = useState('H1');
  const [prices, setPrices] = useState<PriceBar[]>([]);
  const [sma20, setSma20] = useState<any[]>([]);
  const [ema9, setEma9] = useState<any[]>([]);
  const [prediction, setPrediction] = useState<any>(null);
  
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState('');

  const loadChartData = async () => {
    setLoading(true);
    setError('');
    try {
      // 1. Fetch prices
      const priceData = await marketService.getPrices(symbol, timeframe);
      setPrices(priceData);

      // 2. Fetch indicators (to build SMA 20 / EMA 9 arrays)
      const indData = await marketService.getIndicators(symbol, timeframe);
      if (indData && indData.length > 0) {
        const smaArray = indData.map((d: any) => ({
          time: d.timestamp,
          value: d.sma_20
        })).filter((d: any) => d.value !== null);

        const emaArray = indData.map((d: any) => ({
          time: d.timestamp,
          value: d.ema_9
        })).filter((d: any) => d.value !== null);

        setSma20(smaArray);
        setEma9(emaArray);
      }

      // 3. Fetch latest prediction & LLM rationale
      try {
        const pred = await aiService.predict(symbol, timeframe);
        setPrediction(pred);
      } catch (pe) {
        console.error("AI inference error", pe);
      }
    } catch (e: any) {
      console.error("Error loading chart", e);
      if (!e.response) {
        setError('Connection to the Trading Intelligence Backend failed. Please verify that the python backend server is running on http://127.0.0.1:8000 (run "python run.py" in the backend directory).');
      } else {
        setError('Could not fetch price data for symbol. Try syncing with the server.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await marketService.sync(symbol, timeframe, 300);
      await loadChartData();
    } catch (e) {
      setError('Sync failed. Check MT5 connection or fallback status.');
    } finally {
      setSyncing(false);
    }
  };

  const triggerTraining = async () => {
    setSyncing(true);
    try {
      await aiService.train(symbol, timeframe);
      alert('Machine Learning model training completed successfully!');
      await loadChartData();
    } catch (e: any) {
      alert(`Training failed: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    loadChartData();
  }, [symbol, timeframe]);

  return (
    <DashboardLayout>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e1e24] pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Market Explorer</h1>
          <p className="text-zinc-400 text-sm">Analyze price bars, technical indicators, and real-time AI stances.</p>
        </div>

        {/* Inputs */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Symbol selector */}
          <select 
            value={symbol} 
            onChange={(e) => setSymbol(e.target.value)}
            className="bg-[#0c0c0f] border border-[#1e1e24] rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-blue-500"
          >
            <option value="XAUUSD">XAUUSD (Gold - MT5)</option>
            <option value="GBPUSD">GBPUSD (Pound / US Dollar - MT5)</option>
            <option value="EURUSD">EURUSD (Euro / US Dollar - MT5)</option>
            <option value="USDJPY">USDJPY (US Dollar / Yen - MT5)</option>
            <option value="DXY">DXY (US Dollar Index - Yahoo)</option>
          </select>

          {/* Timeframe selector */}
          <select 
            value={timeframe} 
            onChange={(e) => setTimeframe(e.target.value)}
            className="bg-[#0c0c0f] border border-[#1e1e24] rounded-lg px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:border-blue-500"
          >
            <option value="M5">5 Minutes (M5)</option>
            <option value="M15">15 Minutes (M15)</option>
            <option value="H1">1 Hour (H1)</option>
            <option value="D1">Daily (D1)</option>
          </select>

          <button 
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center space-x-1.5 px-3 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 rounded-lg text-sm transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync Data</span>
          </button>

          <button 
            onClick={triggerTraining}
            disabled={syncing}
            className="flex items-center space-x-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm transition-all disabled:opacity-50"
          >
            <Cpu className="h-4 w-4" />
            <span>Train ML</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-lg flex items-center space-x-3 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="h-[450px] flex items-center justify-center border border-[#1e1e24] bg-[#0c0c0f] rounded-xl">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-10 w-8 border-b-2 border-blue-500" />
            <p className="text-zinc-500 text-sm">Fetching and plotting candle data...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Candle Chart */}
          <TVChart data={prices} sma20Data={sma20} ema9Data={ema9} />

          {/* AI Predictor & LLM Analysis block */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Stance Indicator Card */}
            <div className="card-premium p-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-[#1e1e24] pb-3">
                  <span className="text-xs font-semibold text-zinc-400 uppercase">AI Signal Output</span>
                  <Activity className="h-4 w-4 text-blue-500" />
                </div>

                <div className="space-y-1">
                  <p className="text-zinc-500 text-xs uppercase font-semibold">Consensus Stance</p>
                  <h3 className={`text-4xl font-extrabold tracking-tight ${
                    prediction?.direction === 'UP' ? 'text-emerald-500' : prediction?.direction === 'DOWN' ? 'text-rose-500' : 'text-zinc-400'
                  }`}>
                    {prediction?.direction === 'UP' ? 'BUY / BULLISH' : prediction?.direction === 'DOWN' ? 'SELL / BEARISH' : 'HOLD / NEUTRAL'}
                  </h3>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-[#1e1e24] pt-4 mt-6">
                <div>
                  <p className="text-zinc-500 text-[10px] uppercase font-semibold">ML Confidence</p>
                  <p className="text-lg font-bold text-zinc-100">{((prediction?.confidence ?? 0) * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-[10px] uppercase font-semibold">Direction Prob</p>
                  <p className="text-lg font-bold text-zinc-100">{((prediction?.probability ?? 0.5) * 100).toFixed(0)}% UP</p>
                </div>
              </div>
            </div>

            {/* Narrative Rationale Card */}
            <div className="lg:col-span-2 card-premium p-6 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-3">
                  <HelpCircle className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-bold">Gemini LLM Technical Interpretation</span>
                </div>
                <p className="text-zinc-300 text-sm leading-relaxed italic">
                  &ldquo;{prediction?.llm_rationale || "No explanation model generated yet. Train model and ensure Gemini API key is configured in backend settings to run narrative analysis."}&rdquo;
                </p>
              </div>

              <div className="text-xs text-zinc-500 bg-[#09090b]/60 p-2.5 rounded border border-[#1e1e24]">
                Note: Predictions calculate probability of upward return in the next 5 intervals. Combine AI signals with strict stop losses.
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
