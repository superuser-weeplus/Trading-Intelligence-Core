import React, { useState, useEffect } from 'react';
import { monitorService, DataQualityItem } from '@/services/monitor_service';
import { ShieldCheck, ChevronRight, Layers, AlertOctagon, RefreshCw, Globe } from 'lucide-react';

export const DataQualityView: React.FC = () => {
  const [qualityData, setQualityData] = useState<DataQualityItem[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>('DXY');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchQuality = async () => {
      setLoading(true);
      const res = await monitorService.getDataQuality();
      setQualityData(res);
      setLoading(false);
    };
    fetchQuality();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 98) return 'bg-emerald-500 text-emerald-400 border-emerald-500/30';
    if (score >= 90) return 'bg-amber-500 text-amber-400 border-amber-500/30';
    return 'bg-rose-500 text-rose-400 border-rose-500/30';
  };

  const selectedItem = qualityData.find((q) => q.symbol === selectedSymbol) || qualityData[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            หน้าจอที่ 4 : Data Quality Check
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            รายงานวิเคราะห์คุณภาพข้อมูลและความสมบูรณ์ของไฟล์ราคา (Data Health)
          </p>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400">กำลังวิเคราะห์คะแนนคุณภาพข้อมูล...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* List of Symbol Quality Meters */}
          <div className="lg:col-span-2 space-y-4">
            {qualityData.map((item) => {
              const isSelected = selectedSymbol === item.symbol;
              return (
                <div
                  key={item.symbol}
                  onClick={() => setSelectedSymbol(item.symbol)}
                  className={`bg-slate-900/90 border rounded-xl p-5 cursor-pointer transition-all duration-200 shadow-lg ${
                    isSelected
                      ? 'border-cyan-500/80 ring-2 ring-cyan-500/20 bg-slate-800/80'
                      : 'border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-slate-100">{item.symbol}</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${getScoreColor(item.score).split(' ')[1]} ${getScoreColor(item.score).split(' ')[2]}`}>
                        {item.score}% Quality Score
                      </span>
                    </div>
                    <ChevronRight className={`w-5 h-5 transition-transform ${isSelected ? 'rotate-90 text-cyan-400' : 'text-slate-500'}`} />
                  </div>

                  {/* Visual Progress Bar */}
                  <div className="space-y-1.5">
                    <div className="w-full bg-slate-950 rounded-full h-3.5 p-0.5 border border-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${getScoreColor(item.score).split(' ')[0]}`}
                        style={{ width: `${item.score}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 font-mono">
                      <span>0%</span>
                      <span className="font-bold">{item.score}%</span>
                      <span>100%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Detailed Breakdown Card when clicked */}
          <div className="lg:col-span-1">
            {selectedItem && (
              <div className="bg-slate-900/95 border border-slate-800 rounded-xl p-6 shadow-xl sticky top-6 space-y-6">
                <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                  <h3 className="font-bold text-lg text-slate-100 flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-cyan-400" />
                    รายละเอียดสัญลักษณ์: {selectedItem.symbol}
                  </h3>
                  <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-2 py-1 rounded border border-cyan-800">
                    {selectedItem.score}% Score
                  </span>
                </div>

                <div className="space-y-4 text-sm">
                  {/* Duplicate */}
                  <div className="flex items-center justify-between bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
                    <span className="text-slate-400 font-medium flex items-center gap-2">
                      <Layers className="w-4 h-4 text-slate-400" />
                      Duplicate
                    </span>
                    <span className={`font-mono font-bold text-base ${selectedItem.duplicates > 0 ? 'text-rose-400' : 'text-slate-100'}`}>
                      {selectedItem.duplicates}
                    </span>
                  </div>

                  {/* Gap */}
                  <div className="flex items-center justify-between bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
                    <span className="text-slate-400 font-medium flex items-center gap-2">
                      <AlertOctagon className="w-4 h-4 text-amber-400" />
                      Gap
                    </span>
                    <span className={`font-mono font-bold text-base ${selectedItem.gaps > 0 ? 'text-amber-400' : 'text-slate-100'}`}>
                      {selectedItem.gaps}
                    </span>
                  </div>

                  {/* Resampled */}
                  <div className="flex items-center justify-between bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
                    <span className="text-slate-400 font-medium flex items-center gap-2">
                      <RefreshCw className="w-4 h-4 text-blue-400" />
                      Resampled
                    </span>
                    <span className="font-mono font-bold text-base text-blue-400">
                      {selectedItem.resampled}
                    </span>
                  </div>

                  {/* Timezone */}
                  <div className="flex items-center justify-between bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
                    <span className="text-slate-400 font-medium flex items-center gap-2">
                      <Globe className="w-4 h-4 text-emerald-400" />
                      Timezone
                    </span>
                    <span className="font-mono font-bold text-base text-emerald-400">
                      {selectedItem.timezone}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
