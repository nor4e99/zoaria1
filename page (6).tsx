'use client';

import { create } from 'zustand';
import { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastState {
  toasts: Toast[];
  addToast: (message: string, type?: ToastType) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  addToast: (message, type = 'info') => {
    const id = Math.random().toString(36).slice(2);
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 4000);
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

export const toast = {
  success: (msg: string) => useToastStore.getState().addToast(msg, 'success'),
  error:   (msg: string) => useToastStore.getState().addToast(msg, 'error'),
  warning: (msg: string) => useToastStore.getState().addToast(msg, 'warning'),
  info:    (msg: string) => useToastStore.getState().addToast(msg, 'info'),
};

const icons = {
  success: <CheckCircle className="w-5 h-5 text-green-500" />,
  error:   <XCircle    className="w-5 h-5 text-red-500" />,
  warning: <AlertCircle className="w-5 h-5 text-amber-500" />,
  info:    <AlertCircle className="w-5 h-5 text-brand-500" />,
};

const styles: Record<ToastType, string> = {
  success: 'border-green-200 bg-green-50',
  error:   'border-red-200 bg-red-50',
  warning: 'border-amber-200 bg-amber-50',
  info:    'border-brand-200 bg-brand-50',
};

export function Toaster() {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            'flex items-start gap-3 px-4 py-3 rounded-2xl border shadow-card-hover',
            'pointer-events-auto animate-slide-up min-w-[280px] max-w-[380px]',
            styles[t.type]
          )}
        >
          {icons[t.type]}
          <p className="text-sm font-medium text-obsidian-800 flex-1">{t.message}</p>
          <button onClick={() => removeToast(t.id)} className="text-obsidian-400 hover:text-obsidian-600 mt-0.5">
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
