'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell, MessageSquare, Calendar, LayoutDashboard,
  ChevronDown, LogOut, Settings, User, PawPrint,
  Search, Menu, X, Globe, BookOpen, Stethoscope, ShieldCheck
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useNotificationStore } from '@/store/notificationStore';
import { useT, useLangStore } from '@/hooks/useTranslation';
import { authApi } from '@/lib/api';
import { cn } from '@/lib/utils';
import Cookies from 'js-cookie';

const ZoariaLogo = () => (
  <Link href="/" className="flex items-center gap-2 group">
    <div className="w-8 h-8 rounded-xl bg-brand-500 flex items-center justify-center shadow-glow group-hover:shadow-glow-lg transition-shadow">
      <PawPrint className="w-4 h-4 text-white" strokeWidth={2.5} />
    </div>
    <span className="font-display font-semibold text-lg text-obsidian-900 tracking-tight">
      ZOARIA
    </span>
  </Link>
);

const LangSwitch = () => {
  const { lang, setLang } = useLangStore();
  return (
    <button
      onClick={() => setLang(lang === 'en' ? 'bg' : 'en')}
      className="flex items-center gap-1.5 text-xs font-semibold text-obsidian-500
                 hover:text-brand-600 px-2.5 py-1.5 rounded-xl hover:bg-brand-50
                 transition-all border border-transparent hover:border-brand-200"
    >
      <Globe className="w-3.5 h-3.5" />
      <span>{lang.toUpperCase()}</span>
    </button>
  );
};

/* ─── Guest Navbar ──────────────────────────────────────────────────────── */
export function GuestNavbar() {
  const t = useT();
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { label: t('nav.forOwners'), href: '/for-owners' },
    { label: t('nav.forVets'),   href: '/for-vets' },
    { label: t('nav.hub'),       href: '/hub' },
    { label: t('nav.findVet'),   href: '/find-vet' },
  ];

  return (
    <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-sage-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <ZoariaLogo />

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <Link key={l.href} href={l.href}
                className="nav-link text-sm px-4 py-2 rounded-xl">
                {l.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <LangSwitch />
            <Link href="/login" className="btn-ghost text-sm">
              {t('nav.login')}
            </Link>
            <Link href="/register" className="btn-primary text-sm py-2 px-4">
              {t('nav.register')}
            </Link>
            {/* Mobile menu */}
            <button className="md:hidden p-2 rounded-xl hover:bg-sage-50" onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden border-t border-sage-100 overflow-hidden"
          >
            <div className="px-4 py-3 flex flex-col gap-1">
              {links.map((l) => (
                <Link key={l.href} href={l.href}
                  className="nav-link" onClick={() => setMenuOpen(false)}>
                  {l.label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}

/* ─── Dashboard Navbar ──────────────────────────────────────────────────── */
export function DashboardNavbar() {
  const t = useT();
  const { user, clearAuth } = useAuthStore();
  const { unreadCount } = useNotificationStore();
  const [accountOpen, setAccountOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const isVet   = user?.role === 'vet';
  const isAdmin = user?.role === 'admin';

  const ownerLinks = [
    { label: t('nav.pets'),         href: '/pets',          icon: PawPrint },
    { label: t('nav.findVet'),      href: '/find-vet',      icon: Search },
    { label: t('nav.messages'),     href: '/messages',      icon: MessageSquare },
    { label: t('nav.appointments'), href: '/appointments',  icon: Calendar },
    { label: 'Hub',                 href: '/hub',           icon: BookOpen },
  ];
  const adminLinks = [
    { label: 'Vet Approvals', href: '/admin/vets',  icon: Stethoscope },
    { label: 'Users',         href: '/admin/users', icon: ShieldCheck },
  ];
  const dashHref = isAdmin ? '/admin' : isVet ? '/vet' : '/dashboard';
  const navLinks = [
    { label: t('nav.dashboard'), href: dashHref, icon: LayoutDashboard },
    ...(isAdmin ? adminLinks : ownerLinks),
  ];

  const handleLogout = async () => {
    try {
      const refresh = Cookies.get('refresh_token') || localStorage.getItem('refresh_token') || '';
      await authApi.logout(refresh);
    } catch {}
    clearAuth();
    router.push('/login');
  };

  return (
    <nav className="sticky top-0 z-40 bg-white/90 backdrop-blur-xl border-b border-sage-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-6">
            <ZoariaLogo />
            {/* Desktop nav links */}
            <div className="hidden lg:flex items-center gap-1">
              {navLinks.map(({ label, href, icon: Icon }) => (
                <Link
                  key={href} href={href}
                  className={cn('nav-link', pathname.startsWith(href) && 'active')}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <LangSwitch />

            {/* Notifications bell */}
            <Link href="/notifications" className="relative p-2.5 rounded-xl hover:bg-sage-50 transition-colors">
              <Bell className="w-5 h-5 text-obsidian-500" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-red-500 text-white
                                 text-[10px] font-bold rounded-full flex items-center justify-center
                                 animate-pulse-soft">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Link>

            {/* Account dropdown */}
            <div className="relative">
              <button
                onClick={() => setAccountOpen(!accountOpen)}
                className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-2xl
                           hover:bg-sage-50 transition-colors border border-transparent
                           hover:border-sage-200"
              >
                <div className="w-8 h-8 rounded-xl bg-brand-100 flex items-center justify-center overflow-hidden">
                  {user?.profile?.profile_image ? (
                    <img src={user.profile.profile_image} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-brand-700 font-semibold text-sm">
                      {user?.profile?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase()}
                    </span>
                  )}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-semibold text-obsidian-800 leading-tight">
                    {user?.profile?.name || 'Account'}
                  </p>
                  <p className="text-xs text-obsidian-400 capitalize">{user?.subscription?.plan || 'basic'}</p>
                </div>
                <ChevronDown className={cn('w-4 h-4 text-obsidian-400 transition-transform', accountOpen && 'rotate-180')} />
              </button>

              <AnimatePresence>
                {accountOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.96 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 top-full mt-2 w-52 bg-white rounded-2xl
                               border border-sage-200 shadow-card-hover overflow-hidden z-50"
                    onMouseLeave={() => setAccountOpen(false)}
                  >
                    <div className="p-2">
                      <Link href="/account" className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-sage-50 text-sm text-obsidian-700"
                        onClick={() => setAccountOpen(false)}>
                        <User className="w-4 h-4 text-brand-500" /> {t('nav.account')}
                      </Link>
                      <Link href="/account?tab=subscription" className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-sage-50 text-sm text-obsidian-700"
                        onClick={() => setAccountOpen(false)}>
                        <Settings className="w-4 h-4 text-brand-500" /> Settings
                      </Link>
                    </div>
                    <div className="border-t border-sage-100 p-2">
                      <button onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-red-50 text-sm text-red-600">
                        <LogOut className="w-4 h-4" /> {t('nav.logout')}
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile bottom nav */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-xl border-t border-sage-200">
        <div className="flex items-center justify-around px-1 py-1">
          {navLinks.slice(0, 5).map(({ label, href, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + '/');
            return (
              <Link key={href} href={href}
                className={cn(
                  'flex flex-col items-center gap-0.5 px-2 py-2 rounded-xl transition-all min-w-0 flex-1',
                  active ? 'text-brand-600' : 'text-obsidian-400 hover:text-obsidian-600'
                )}>
                <Icon className={cn('w-5 h-5', active && 'stroke-[2.5]')} />
                <span className="text-[9px] font-semibold truncate w-full text-center leading-tight">{label}</span>
              </Link>
            );
          })}
          <Link href="/notifications"
            className={cn('flex flex-col items-center gap-0.5 px-2 py-2 rounded-xl relative flex-1',
              pathname.startsWith('/notifications') ? 'text-brand-600' : 'text-obsidian-400'
            )}>
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-2 w-3.5 h-3.5 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
            <span className="text-[9px] font-semibold">Alerts</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
