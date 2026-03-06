'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { getAccessToken } from '@/lib/api';

/** Call this in any page/layout that requires authentication.
 *  Auto-redirects to /login if no token is present.
 *  Hydrates user store from /auth/me/ on first load.
 */
export function useAuth(options?: { require?: 'owner' | 'vet' | 'admin' }) {
  const router   = useRouter();
  const { user, setAuth, clearAuth } = useAuthStore();
  const token    = getAccessToken();

  const { data, isLoading, error } = useQuery({
    queryKey: ['me'],
    queryFn:  () => authApi.me().then(r => r.data),
    enabled:  !!token && !user,
    retry:    false,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (!token) {
      router.replace('/login');
      return;
    }
    if (error) {
      clearAuth();
      router.replace('/login');
    }
  }, [token, error]);

  useEffect(() => {
    if (data && !user) {
      // Re-hydrate user from API (e.g. after hard refresh)
      const stored = useAuthStore.getState();
      if (stored.accessToken) {
        setAuth(data, stored.accessToken, stored.refreshToken!);
      }
    }
  }, [data]);

  // Role guard
  useEffect(() => {
    if (user && options?.require && user.role !== options.require && user.role !== 'admin') {
      router.replace('/dashboard');
    }
  }, [user, options?.require]);

  return { user: user || data, isLoading: isLoading || (!user && !!token) };
}
