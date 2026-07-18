import React from 'react';
import { SummaryMetricsData } from '@/services/monitor_service';
import { Layers, Database, Hash, CheckCircle2, ShieldCheck } from 'lucide-react';

interface DashboardSummaryBarProps {
  metrics: SummaryMetricsData;
}

export const DashboardSummaryBar: React.FC<DashboardSummaryBarProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {/* Symbols */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between space-y-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-blue-400" />
          Symbols
        </span>
        <span className="text-2xl font-mono font-bold text-slate-100">{metrics.symbols}</span>
      </div>

      {/* Datasets */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between space-y-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Database className="w-4 h-4 text-cyan-400" />
          Datasets
        </span>
        <span className="text-2xl font-mono font-bold text-slate-100">{metrics.datasets}</span>
      </div>

      {/* Total Candles */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between space-y-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Hash className="w-4 h-4 text-purple-400" />
          Total Candles
        </span>
        <span className="text-2xl font-mono font-bold text-purple-400">
          {metrics.total_candles > 1000 ? `${(metrics.total_candles / 1000).toFixed(0)}k+` : metrics.total_candles}
        </span>
      </div>

      {/* Export Success */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between space-y-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          Export Success
        </span>
        <span className="text-2xl font-mono font-bold text-emerald-400">{metrics.export_success_pct}%</span>
      </div>

      {/* Data Quality */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between space-y-2 col-span-2 md:col-span-1">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-amber-400" />
          Data Quality
        </span>
        <span className="text-2xl font-mono font-bold text-amber-400">{metrics.data_quality_pct}%</span>
      </div>
    </div>
  );
};
