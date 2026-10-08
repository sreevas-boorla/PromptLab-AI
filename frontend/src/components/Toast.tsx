import React from 'react';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onClose }) => {
  return (
    <div className="fixed bottom-5 right-5 z-50 space-y-2 max-w-md w-full">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center justify-between p-4 rounded-xl border shadow-xl backdrop-blur transition-all ${
            t.type === 'error'
              ? 'bg-rose-950/90 border-rose-800/80 text-rose-200'
              : t.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-800/80 text-emerald-200'
              : 'bg-slate-900/90 border-slate-700 text-slate-200'
          }`}
          role="alert"
        >
          <div className="flex items-center space-x-3">
            {t.type === 'error' ? (
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            )}
            <span className="text-sm font-medium">{t.message}</span>
          </div>
          <button
            onClick={() => onClose(t.id)}
            className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white"
            aria-label="Dismiss toast"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
};
