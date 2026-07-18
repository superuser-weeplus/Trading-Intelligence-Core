import React, { useState, useEffect } from 'react';
import { monitorService, DataExplorerData } from '@/services/monitor_service';
import { Database, Filter, Calendar, Hash, AlertTriangle, Layers } from 'lucide-react';

export const DataExplorerView: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('XAUUSD');
  const [timeframe, setTimeframe] = useState<string>('H1');
  const [data, setData] = useState<DataExplorerData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const symbols = ['XAUUSD', 'GBPUSD', 'EURUSD', 'DXY'];
  const timeframes = ['M1', 'M5', 'M15', 'H1', 'H4', 'D1'];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const res = await monitorService.getDataExplorer(symbol, timeframe);
      setData(res);
      setLoading(false);
    };
    fetchData();
  }, [symbol, timeframe]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" />
            หน้าจอที่ 2 : Data Explorer (สำหรับ Data Engineer)
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            สำรวจสถิติชุดข้อมูลแท่งราคาและช่วงเวลาที่จัดเก็บ
          </p>
        </div>

        {/* Dropdown Filters */}
        <div className="flex items-center space-x-3 bg-slate-900/90 p-2 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 px-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-400 uppercase">Symbol</span>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="bg-slate-950 text-slate-100 text-sm font-semibold rounded-lg px-3 py-1.5 border border-slate-700 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {symbols.map((s) => (
                <option key={s} value={s}>
                  ▼ {s}
                </option>
              ))}
            </select>
          </div>

          <div className="h-6 w-px bg-slate-800" />

          <div className="flex items-center gap-2 px-2">
            <span className="text-xs font-semibold text-slate-400 uppercase">Timeframe</span>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="bg-slate-950 text-slate-100 text-sm font-semibold rounded-lg px-3 py-1.5 border border-slate-700 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {timeframes.map((tf) => (
                <option key={tf} value={tf}>
                  ▼ {tf}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Stats Display */}
      {loading ? (
        <div className="flex items-center justify-center p-12 bg-slate-900/40 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-sm animate-pulse">กำลังโหลดสถิติชุดข้อมูล...</span>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {/* Total Rows */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
              <Hash className="w-4 h-4 text-cyan-400" />
              Rows
            </span>
            <span className="text-3xl font-mono font-bold text-slate-100">{data.rows.toLocaleString()}</span>
          </div>

          {/* First Date */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
              <Calendar className="w-4 h-4 text-emerald-400" />
              First Date
            </span>
            <span className="text-xl font-mono font-bold text-emerald-400">{data.first}</span>
          </div>

          {/* Last Date */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
              <Calendar className="w-4 h-4 text-blue-400" />
              Last Date
            </span>
            <span className="text-xl font-mono font-bold text-blue-400">{data.last}</span>
          </div>

          {/* Missing Gaps */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Missing
            </span>
            <span className={`text-3xl font-mono font-bold ${data.missing > 0 ? 'text-amber-400' : 'text-slate-100'}`}>
              {data.missing}
            </span>
          </div>

          {/* Duplicates */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-3">
            <span className="text-xs font-semibold text-slate-400 uppercase flex items-center gap-2">
              <Layers className="w-4 h-4 text-rose-400" />
              Duplicate
            </span>
            <span className={`text-3xl font-mono font-bold ${data.duplicate > 0 ? 'text-rose-400' : 'text-slate-100'}`}>
              {data.duplicate}
            </span>
          </div>
        </div>
      ) : null}

      {/* Data Freshness Indicator Banner */}
      {data && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <span className="h-3 w-3 rounded-full bg-emerald-500 animate-ping" />
            <div>
              <h4 className="text-sm font-bold text-slate-100">Data Freshness Indicator</h4>
              <p className="text-xs text-slate-400">สถานะความใหม่ของชุดข้อมูลที่อัปเดตล่าสุด</p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-right">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Freshness</span>
              <span className="text-sm font-mono font-bold text-emerald-400">{data.freshness || '3 minutes ago'}</span>
            </div>
            <div className="h-8 w-px bg-slate-800" />
            <div className="text-right">
              <span className="text-xs text-slate-400 font-semibold block uppercase">Last Updated</span>
              <span className="text-sm font-mono font-bold text-cyan-400">{data.last_updated || '2026-07-18 16:13'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
