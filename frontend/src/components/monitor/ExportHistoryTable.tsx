import React, { useState, useEffect } from 'react';
import { monitorService, ExportHistoryItem } from '@/services/monitor_service';
import { History, FileText, CheckCircle2 } from 'lucide-react';

export const ExportHistoryTable: React.FC = () => {
  const [history, setHistory] = useState<ExportHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      const res = await monitorService.getExportHistory();
      setHistory(res);
      setLoading(false);
    };
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <History className="w-5 h-5 text-amber-400" />
            หน้าจอที่ 3 : Export History
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            ตารางบันทึกประวัติคำสั่ง Export ย้อนหลังของระบบ
          </p>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        {loading ? (
          <div className="p-8 text-center text-slate-400">กำลังโหลดประวัติ Export...</div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-slate-500">ยังไม่มีประวัติการ Export</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-950/80 border-b border-slate-800 text-xs uppercase text-slate-400 font-semibold tracking-wider">
                  <th className="py-3.5 px-6">เวลา</th>
                  <th className="py-3.5 px-6">Symbol</th>
                  <th className="py-3.5 px-6">TF</th>
                  <th className="py-3.5 px-6">Bars</th>
                  <th className="py-3.5 px-6 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm font-mono">
                {history.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-6 text-slate-400">{row.time}</td>
                    <td className="py-3.5 px-6 font-bold text-slate-100 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-500" />
                      {row.symbol}
                    </td>
                    <td className="py-3.5 px-6">
                      <span className="bg-slate-800 text-cyan-400 px-2 py-0.5 rounded font-semibold text-xs">
                        {row.tf}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-200 font-bold">{row.bars.toLocaleString()}</td>
                    <td className="py-3.5 px-6 text-center">
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                        <CheckCircle2 className="w-4 h-4" />
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
