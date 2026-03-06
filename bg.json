import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { setTokens, clearTokens } from '@/lib/api';

export interface UserProfile {
  name: string;
  bio: string;
  location: string;
  profile_image: string;
  language: 'en' | 'bg';
}

export interface User {
  id: number;
  email: string;
  role: 'owner' | 'vet' | 'admin';
  email_verified: boolean;
  profile: UserProfile;
  subscription: { plan: string; end_date?: string };
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;

  setAuth: (user: User, access: string, refresh: string) => void;
  updateUser: (data: Partial<User>) => void;
  clearAuth: () => void;
  setLoading: (v: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,

      setAuth: (user, access, refresh) => {
        setTokens(access, refresh);
        set({ user, accessToken: access, refreshToken: refresh });
      },

      updateUser: (data) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...data } : null,
        })),

      clearAuth: () => {
        clearTokens();
        set({ user: null, accessToken: null, refreshToken: null });
      },

      setLoading: (v) => set({ isLoading: v }),
    }),
    {
      name: 'zoaria-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
