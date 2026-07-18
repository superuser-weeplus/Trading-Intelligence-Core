'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../../components/DashboardLayout';
import { alertService, AlertRule, AlertLog } from '../../services/api';
import { 
  Bell, 
  PlusCircle, 
  Activity, 
  History, 
  RefreshCw, 
  CheckSquare,
  AlertTriangle
} from 'lucide-react';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertRule[]>([]);
  const [logs, setLogs] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  // Form states
  const [symbol, setSymbol] = useState('EURUSD');
  const [metric, setMetric] = useState('PRICE');
  const [operator, setOperator] = useState('>');
  const [threshold, setThreshold] = useState(1.1200);

  const loadAlerts = async () => {
    try {
      const activeAlerts = await alertService.getAlerts();
      setAlerts(activeAlerts);
      const alertLogs = await alertService.getLogs();
      setLogs(alertLogs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await alertService.createAlert({
        symbol,
        metric,
        operator,
        threshold
      });
      alert('Alert rule configured successfully.');
      loadAlerts();
    } catch (err: any) {
      alert(`Error creating alert: ${err.message}`);
    }
  };

  const handleCheck = async () => {
    setChecking(true);
    try {
      const res = await alertService.checkAlerts();
      alert(`Alert scanner completed. Triggered ${res.triggered_count} alerts.`);
      loadAlerts();
    } catch (err: any) {
      alert(`Scanner error: ${err.message}`);
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  return (
    <DashboardLayout>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e1e24] pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Alert Console</h1>
          <p className="text-zinc-400 text-sm">Define, monitor, and review market trigger conditions.</p>
        </div>

        <button
          onClick={handleCheck}
          disabled={checking}
          className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-all disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${checking ? 'animate-spin' : ''}`} />
          <span>Scan Active Rules</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Create alert rule */}
        <div className="card-premium p-6 space-y-6 h-fit">
          <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-3">
            <PlusCircle className="h-4 w-4 text-blue-500" />
            <h2 className="text-md font-bold">Configure Alert Trigger</h2>
          </div>

          <form onSubmit={handleCreate} className="space-y-4 text-sm">
            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Symbol</label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 focus:outline-none"
              >
                <option value="XAUUSD">XAUUSD</option>
                <option value="GBPUSD">GBPUSD</option>
                <option value="EURUSD">EURUSD</option>
                <option value="USDJPY">USDJPY</option>
                <option value="DXY">DXY</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Metric</label>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 focus:outline-none"
                >
                  <option value="PRICE">PRICE</option>
                  <option value="RSI">RSI (14)</option>
                  <option value="ATR">ATR (14)</option>
                </select>
              </div>

              <div className="flex flex-col space-y-1.5">
                <label className="text-xs font-semibold text-zinc-500 uppercase">Condition</label>
                <select
                  value={operator}
                  onChange={(e) => setOperator(e.target.value)}
                  className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 focus:outline-none"
                >
                  <option value=">">&gt; (Greater than)</option>
                  <option value="<">&lt; (Less than)</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col space-y-1.5">
              <label className="text-xs font-semibold text-zinc-500 uppercase">Threshold value</label>
              <input
                type="number"
                step="0.0001"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="bg-[#09090b] border border-[#1e1e24] rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg text-sm transition-all"
            >
              Configure Rule
            </button>
          </form>
        </div>

        {/* Right: Active Alert Rules & Trigger Logs */}
        <div className="lg:col-span-2 space-y-8">
          {/* Active Rules */}
          <div className="card-premium p-6">
            <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-4 mb-4">
              <CheckSquare className="h-5 w-5 text-blue-500" />
              <h3 className="font-bold text-zinc-100">Configured Conditions</h3>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-zinc-400 border-collapse">
                <thead>
                  <tr className="border-b border-[#1e1e24] text-zinc-500 uppercase tracking-wider font-semibold">
                    <th className="py-2">Asset</th>
                    <th className="py-2">Metric</th>
                    <th className="py-2">Condition</th>
                    <th className="py-2">Trigger Threshold</th>
                    <th className="py-2 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e1e24]/60">
                  {alerts.map((a) => (
                    <tr key={a.id} className="hover:bg-zinc-800/10">
                      <td className="py-3 font-semibold text-zinc-200">{a.symbol}</td>
                      <td className="py-3 uppercase text-zinc-400">{a.metric}</td>
                      <td className="py-3 font-mono">{a.operator === '>' ? 'Greater than' : 'Less than'}</td>
                      <td className="py-3 font-mono">${a.threshold.toFixed(4)}</td>
                      <td className="py-3 text-right">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          a.status === 'ACTIVE' 
                            ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' 
                            : a.status === 'TRIGGERED'
                            ? 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                            : 'bg-zinc-800 text-zinc-500 border-zinc-700'
                        }`}>{a.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Trigger logs */}
          <div className="card-premium p-6">
            <div className="flex items-center space-x-2 border-b border-[#1e1e24] pb-4 mb-4">
              <History className="h-5 w-5 text-amber-500" />
              <h3 className="font-bold text-zinc-100">Alert Notification Logs</h3>
            </div>

            {logs.length === 0 ? (
              <p className="text-zinc-500 text-center py-6 text-sm">No alerts triggered yet.</p>
            ) : (
              <div className="space-y-3">
                {logs.map((log) => (
                  <div key={log.id} className="flex items-start space-x-3 text-xs bg-[#09090b]/40 border border-[#1e1e24] p-3 rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <p className="font-semibold text-zinc-200 leading-normal">{log.message}</p>
                      <p className="text-[10px] text-zinc-500">{new Date(log.triggered_at).toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
