import React from 'react';
import { MarketSnapshotItem } from '@/services/monitor_service';
import { TrendingUp, TrendingDown, Activity, Clock } from 'lucide-react';

interface TodayMarketSnapshotProps {
  snapshot: MarketSnapshotItem[];
}

export const TodayMarketSnapshot: React.FC<TodayMarketSnapshotProps> = ({ snapshot }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
          <Activity className="w-5 h-5 text-cyan-400" />
          Today's Market Snapshot (Instant Status)
        </h3>
        <span className="text-xs text-slate-400">Live indicators preview</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {snapshot.map((item) => (
          <div
            key={item.symbol}
            className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-4 space-y-3 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between">
              <span className="font-extrabold text-base text-slate-100">{item.symbol}</span>
              <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                <Clock className="w-3 h-3 text-slate-500" />
                {item.last_update}
              </span>
            </div>

            <div className="text-2xl font-mono font-bold text-slate-50">
              {item.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
            </div>

            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/60 text-xs font-semibold">
              <div className="flex items-center justify-between bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
                <span className="text-slate-400">H1</span>
                <span className={`flex items-center gap-0.5 ${item.h1_trend === 'Bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {item.h1_trend === 'Bullish' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {item.h1_trend}
                </span>
              </div>

              <div className="flex items-center justify-between bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
                <span className="text-slate-400">H4</span>
                <span className={`flex items-center gap-0.5 ${item.h4_trend === 'Bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {item.h4_trend === 'Bullish' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {item.h4_trend}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
