'use client';

import React, { useState, useEffect } from 'react';
import { 
  monitorService, 
  SystemHealthData, 
  SummaryMetricsData, 
  SystemAlertItem, 
  MarketSnapshotItem 
} from '../services/monitor_service';
import { SystemHealthView } from '../components/monitor/SystemHealthView';
import { DataExplorerView } from '../components/monitor/DataExplorerView';
import { ExportHistoryTable } from '../components/monitor/ExportHistoryTable';
import { DataQualityView } from '../components/monitor/DataQualityView';
import { DashboardSummaryBar } from '../components/monitor/DashboardSummaryBar';
import { SystemAlertsBanner } from '../components/monitor/SystemAlertsBanner';
import { TodayMarketSnapshot } from '../components/monitor/TodayMarketSnapshot';
import { Activity, Database, History, ShieldCheck, RefreshCw } from 'lucide-react';

export default function DataMonitorDashboardPage() {
  const [activeTab, setActiveTab] = useState<'health' | 'explorer' | 'history' | 'quality'>('health');
  
  const [healthData, setHealthData] = useState<SystemHealthData>({
    mt5: { status: 'connected', latency_ms: 18, label: 'Connected (18ms)' },
    supabase: { status: 'connected', latency_ms: 42, label: 'Connected (42ms)' },
    exporter: { status: 'running', label: 'Running' },
    importer: { status: 'running', label: 'Running' },
    last_export: '2026-07-18 16:13',
    last_import: '2026-07-18 16:14'
  });

  const [summaryMetrics, setSummaryMetrics] = useState<SummaryMetricsData>({
    symbols: 4,
    datasets: 24,
    total_candles: 113727,
    export_success_pct: 100,
    data_quality_pct: 99
  });

  const [systemAlerts, setSystemAlerts] = useState<SystemAlertItem[]>([]);
  const [marketSnapshot, setMarketSnapshot] = useState<MarketSnapshotItem[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    setRefreshing(true);
    try {
      const [healthRes, summaryRes, alertsRes, snapshotRes] = await Promise.all([
        monitorService.getSystemHealth(),
        monitorService.getSummaryMetrics(),
        monitorService.getSystemAlerts(),
        monitorService.getMarketSnapshot()
      ]);
      setHealthData(healthRes);
      setSummaryMetrics(summaryRes);
      setSystemAlerts(alertsRes);
      setMarketSnapshot(snapshotRes);
    } catch (e) {
      console.error('Error fetching dashboard data', e);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 15000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'health', label: 'System Health', icon: Activity, badge: healthData.mt5.status === 'connected' ? '🟢 Live' : '🔴 Alert' },
    { id: 'explorer', label: 'Data Explorer', icon: Database },
    { id: 'history', label: 'Export History', icon: History },
    { id: 'quality', label: 'Data Quality Check', icon: ShieldCheck, highlight: true }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 sm:p-8 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            <span className="p-2 bg-cyan-500/10 rounded-xl border border-cyan-500/30 text-cyan-400">
              <Activity className="w-7 h-7" />
            </span>
            Trading Intelligence Platform
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Data Monitor Dashboard — Enterprise Data Foundation & Latency Inspection for Data Engineers
          </p>
        </div>

        <button
          onClick={fetchDashboardData}
          disabled={refreshing}
          className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold px-4 py-2 rounded-xl border border-slate-700 transition-all cursor-pointer shadow-md disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-cyan-400' : ''}`} />
          <span>Refresh Dashboard</span>
        </button>
      </div>

      {/* 1. Top Dashboard Summary Panel */}
      <DashboardSummaryBar metrics={summaryMetrics} />

      {/* 2. System Warnings & Critical Alerts Banner */}
      <SystemAlertsBanner alerts={systemAlerts} />

      {/* 3. Today's Market Snapshot Widget */}
      <TodayMarketSnapshot snapshot={marketSnapshot} />

      {/* 4. Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2 pt-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2.5 px-5 py-3 rounded-xl font-semibold text-sm transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-950 border border-slate-700 text-emerald-400 font-mono">
                  {tab.badge}
                </span>
              )}
              {tab.highlight && (
                <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">
                  Priority
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Tab Content Display */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-2xl backdrop-blur-sm">
        {activeTab === 'health' && <SystemHealthView health={healthData} />}
        {activeTab === 'explorer' && <DataExplorerView />}
        {activeTab === 'history' && <ExportHistoryTable />}
        {activeTab === 'quality' && <DataQualityView />}
      </div>
    </div>
  );
}
