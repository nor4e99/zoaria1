'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import en from '@/i18n/en.json';
import bg from '@/i18n/bg.json';

type Lang = 'en' | 'bg';
const translations: Record<Lang, any> = { en, bg };

interface LangState {
  lang: Lang;
  setLang: (l: Lang) => void;
}

export const useLangStore = create<LangState>()(
  persist(
    (set) => ({
      lang: 'en',
      setLang: (lang) => set({ lang }),
    }),
    { name: 'zoaria-lang' }
  )
);

/** Simple dot-path translation hook */
export function useT() {
  const { lang } = useLangStore();
  const dict = translations[lang];

  return function t(key: string, vars?: Record<string, string | number>): string {
    const parts = key.split('.');
    let val: any = dict;
    for (const p of parts) {
      if (val == null) return key;
      val = val[p];
    }
    if (typeof val !== 'string') return key;
    if (vars) {
      return Object.entries(vars).reduce(
        (str, [k, v]) => str.replace(`{${k}}`, String(v)),
        val
      );
    }
    return val;
  };
}
