'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import { authApi, paymentsApi } from '@/lib/api';
import { useT } from '@/hooks/useTranslation';
import { toast } from '@/components/ui/Toaster';
import { User, CreditCard, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';

const TABS = [
  { key: 'profile',      label: 'Profile',      icon: User },
  { key: 'subscription', label: 'Subscription',  icon: CreditCard },
  { key: 'security',     label: 'Security',      icon: Lock },
];

const PLANS = [
  {
    key: 'basic',
    name: 'Basic',
    price: 'Free',
    pets: '1 pet',
    features: ['Deworming reminders', 'Basic hub access'],
    color: 'border-sage-300',
  },
  {
    key: 'standard',
    name: 'Standard',
    price: '€9.99/mo',
    pets: '2 pets',
    features: ['Feeding plans', 'Vaccination reminders', 'Nutrition tracking'],
    color: 'border-brand-400',
    popular: true,
  },
  {
    key: 'premium',
    name: 'Premium',
    price: '€19.99/mo',
    pets: 'Unlimited pets',
    features: ['Vet chat', 'GPS tracking', 'Medication tracker', 'Full hub access'],
    color: 'border-amber-400',
  },
];

export default function AccountPage() {
  const t = useT();
  const { user, updateUser } = useAuthStore();
  const [tab, setTab] = useState('profile');
  const [saving, setSaving] = useState(false);
  const [upgrading, setUpgrading] = useState<string | null>(null);

  const [profileForm, setProfileForm] = useState({
    name: user?.profile?.name || '',
    bio: user?.profile?.bio || '',
    location: user?.profile?.location || '',
    language: user?.profile?.language || 'en',
  });

  const handleProfileSave = async () => {
    setSaving(true);
    try {
      const res = await authApi.updateProfile(profileForm);
      updateUser({ profile: { ...user!.profile, ...profileForm } });
      toast.success('Profile updated!');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSubscribe = async (plan: string) => {
    setUpgrading(plan);
    try {
      const res = await paymentsApi.subscribe(plan);
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      } else {
        toast.success(`Switched to ${plan} plan!`);
        updateUser({ subscription: { plan } });
      }
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to change plan');
    } finally {
      setUpgrading(null);
    }
  };

  const currentPlan = user?.subscription?.plan || 'basic';

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="font-display text-2xl font-bold text-obsidian-900">Account</h1>
        <p className="text-obsidian-500 mt-1">Manage your profile and subscription</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-sage-100 rounded-2xl w-fit">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button key={key} onClick={() => setTab(key)}
            className={cn('flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all',
              tab === key ? 'bg-white text-brand-700 shadow-card' : 'text-obsidian-500 hover:text-obsidian-700')}>
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {/* Profile tab */}
      {tab === 'profile' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className="zoaria-card space-y-4">
          <h2 className="font-semibold text-obsidian-900">Personal Information</h2>
          <div>
            <label className="label-base">Full Name</label>
            <input value={profileForm.name}
              onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
              className="input-base" placeholder="Your name" />
          </div>
          <div>
            <label className="label-base">Bio</label>
            <textarea value={profileForm.bio}
              onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
              className="input-base resize-none" rows={3} placeholder="Tell us about yourself..." />
          </div>
          <div>
            <label className="label-base">Location</label>
            <input value={profileForm.location}
              onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })}
              className="input-base" placeholder="Sofia, Bulgaria" />
          </div>
          <div>
            <label className="label-base">Preferred Language</label>
            <select value={profileForm.language}
              onChange={(e) => setProfileForm({ ...profileForm, language: e.target.value as 'en' | 'bg' })}
              className="input-base">
              <option value="en">English</option>
              <option value="bg">Български</option>
            </select>
          </div>
          <button onClick={handleProfileSave} disabled={saving} className="btn-primary flex items-center gap-2">
            {saving && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
            {t('common.save')}
          </button>
        </motion.div>
      )}

      {/* Subscription tab */}
      {tab === 'subscription' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-sm text-obsidian-500 mb-4">
            Current plan: <strong className="text-obsidian-900 capitalize">{currentPlan}</strong>
          </p>
          <div className="grid sm:grid-cols-3 gap-4">
            {PLANS.map((plan) => {
              const isCurrent = currentPlan === plan.key;
              return (
                <div key={plan.key}
                  className={cn('zoaria-card border-2 transition-all', plan.color,
                    isCurrent && 'ring-2 ring-brand-500', plan.popular && !isCurrent && 'border-brand-400')}>
                  {plan.popular && (
                    <span className="badge bg-brand-500 text-white mb-3 block w-fit">Most Popular</span>
                  )}
                  <h3 className="font-bold text-obsidian-900 text-lg">{plan.name}</h3>
                  <p className="text-brand-600 font-semibold text-2xl mt-1">{plan.price}</p>
                  <p className="text-sm text-obsidian-500 mb-3">{plan.pets}</p>
                  <ul className="space-y-1.5 mb-4">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-center gap-2 text-sm text-obsidian-700">
                        <span className="text-brand-500">✓</span> {f}
                      </li>
                    ))}
                  </ul>
                  {isCurrent ? (
                    <div className="btn-secondary text-center text-sm py-2 opacity-60 cursor-default">
                      {t('plans.current')}
                    </div>
                  ) : (
                    <button onClick={() => handleSubscribe(plan.key)}
                      disabled={upgrading === plan.key}
                      className="btn-primary w-full text-sm py-2 flex items-center justify-center gap-2">
                      {upgrading === plan.key
                        ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        : t('plans.upgrade')}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Security tab */}
      {tab === 'security' && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <ChangePasswordForm />
        </motion.div>
      )}
    </div>
  );
}

function ChangePasswordForm() {
  const [form, setForm] = useState({ old_password: '', new_password: '', confirm_new_password: '' });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.new_password !== form.confirm_new_password) {
      toast.error('Passwords do not match');
      return;
    }
    setSaving(true);
    try {
      await authApi.changePassword(form);
      toast.success('Password updated!');
      setForm({ old_password: '', new_password: '', confirm_new_password: '' });
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="zoaria-card space-y-4 max-w-md">
      <h2 className="font-semibold text-obsidian-900">Change Password</h2>
      {[
        { key: 'old_password', label: 'Current Password', type: 'password' },
        { key: 'new_password', label: 'New Password', type: 'password' },
        { key: 'confirm_new_password', label: 'Confirm New Password', type: 'password' },
      ].map(({ key, label, type }) => (
        <div key={key}>
          <label className="label-base">{label}</label>
          <input type={type} value={(form as any)[key]}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
            className="input-base" placeholder="••••••••" />
        </div>
      ))}
      <button type="submit" disabled={saving} className="btn-primary flex items-center gap-2">
        {saving && <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
        Update Password
      </button>
    </form>
  );
}
