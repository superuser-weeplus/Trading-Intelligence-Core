import React from 'react';
import { SystemAlertItem } from '@/services/monitor_service';
import { AlertOctagon, AlertTriangle, Info } from 'lucide-react';

interface SystemAlertsProps {
  alerts: SystemAlertItem[];
}

export const SystemAlertsBanner: React.FC<SystemAlertsProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="space-y-3">
      {alerts.map((alert, idx) => {
        const isCritical = alert.severity === 'CRITICAL';
        const isWarning = alert.severity === 'WARNING';
        
        if (alert.code === 'ALL_SYSTEMS_OPERATIONAL') return null;

        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border flex items-start gap-3.5 shadow-lg transition-all ${
              isCritical
                ? 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                : isWarning
                ? 'bg-amber-950/40 border-amber-500/50 text-amber-200'
                : 'bg-blue-950/40 border-blue-500/50 text-blue-200'
            }`}
          >
            {isCritical ? (
              <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            ) : isWarning ? (
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            ) : (
              <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
            )}

            <div className="space-y-0.5">
              <h4 className="font-bold text-sm flex items-center gap-2">
                {isCritical && <span className="text-xs bg-rose-900/80 text-rose-300 px-2 py-0.5 rounded font-mono">🔴 CRITICAL</span>}
                {isWarning && <span className="text-xs bg-amber-900/80 text-amber-300 px-2 py-0.5 rounded font-mono">🟡 WARNING</span>}
                {alert.title}
              </h4>
              <p className="text-xs opacity-90">{alert.message}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
