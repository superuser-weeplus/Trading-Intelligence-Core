import React from 'react';
import { SystemHealthData } from '@/services/monitor_service';
import { Server, Database, RefreshCw, Clock, Activity } from 'lucide-react';

interface SystemHealthProps {
  health: SystemHealthData;
}

export const SystemHealthView: React.FC<SystemHealthProps> = ({ health }) => {
  const getStatusBadge = (status: string, label: string, latencyMs?: number) => {
    const isConnected = status === 'connected' || status === 'running';
    return (
      <div className="flex items-center space-x-2 bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-700/50">
        <span className={`h-3 w-3 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
        <span className={`text-sm font-medium ${isConnected ? 'text-emerald-400' : 'text-red-400'}`}>
          {isConnected ? `🟢 ${label}` : `🔴 ${label}`}
        </span>
        {latencyMs !== undefined && latencyMs > 0 && (
          <span className="text-xs font-mono bg-slate-950 text-cyan-400 px-2 py-0.5 rounded border border-slate-800">
            {latencyMs}ms
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            หน้าจอที่ 1 : System Health
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            สถานะการเชื่อมต่อและการทำงานของระบบท่อส่งข้อมูล (Data Pipeline)
          </p>
        </div>
      </div>

      {/* Grid Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* MT5 Terminal */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-semibold text-sm">MT5 Terminal</span>
            <Server className="w-5 h-5 text-blue-400" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-slate-100">MT5</span>
            {getStatusBadge(health.mt5.status, health.mt5.label, health.mt5.latency_ms)}
          </div>
        </div>

        {/* Supabase Cloud */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-semibold text-sm">Supabase Database</span>
            <Database className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-slate-100">Supabase</span>
            {getStatusBadge(health.supabase.status, health.supabase.label, health.supabase.latency_ms)}
          </div>
        </div>

        {/* Exporter Engine */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-semibold text-sm">Exporter Engine</span>
            <RefreshCw className="w-5 h-5 text-amber-400 animate-spin-slow" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-slate-100">Exporter</span>
            {getStatusBadge(health.exporter.status, health.exporter.label)}
          </div>
        </div>

        {/* Importer Engine */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-semibold text-sm">Importer Engine</span>
            <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin-slow" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-slate-100">Importer</span>
            {getStatusBadge(health.importer.status, health.importer.label)}
          </div>
        </div>
      </div>

      {/* Timestamps Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          ประวัติเวลาส่งออกและนำเข้าล่าสุด (Last Pipeline Execution Timestamps)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center justify-between bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-slate-300 font-medium">Last Export</span>
            <span className="text-lg font-mono font-bold text-cyan-400">{health.last_export}</span>
          </div>

          <div className="flex items-center justify-between bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-slate-300 font-medium">Last Import</span>
            <span className="text-lg font-mono font-bold text-emerald-400">{health.last_import}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
