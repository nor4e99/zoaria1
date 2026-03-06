'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, Trash2, Activity, Calendar, Utensils, Heart, FileText } from 'lucide-react';
import { petsApi, healthApi, feedingApi } from '@/lib/api';
import { BMIIndicator } from '@/components/pets/BMIIndicator';
import { useT } from '@/hooks/useTranslation';
import { cn } from '@/lib/utils';
import { toast } from '@/components/ui/Toaster';

const AVATARS: Record<string, string> = {
  dog: '🐕', cat: '🐈', horse: '🐎', rabbit: '🐇',
  guinea: '🐹', bird: '🦜', fish: '🐠', turtle: '🐢',
};

const TABS = [
  { key: 'overview', label: 'Overview',     icon: Heart },
  { key: 'health',   label: 'Health',       icon: FileText },
  { key: 'feeding',  label: 'Feeding',      icon: Utensils },
  { key: 'activity', label: 'Activity',     icon: Activity },
  { key: 'calendar', label: 'Calendar',     icon: Calendar },
];

export default function PetDetailPage() {
  const t = useT();
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [tab, setTab] = useState('overview');

  const { data: pet, isLoading } = useQuery({
    queryKey: ['pet', id],
    queryFn: () => petsApi.get(Number(id)).then((r) => r.data),
  });

  const { data: bmiData } = useQuery({
    queryKey: ['bmi', id],
    queryFn: () => petsApi.bmi(Number(id)).then((r) => r.data),
    enabled: !!pet?.weight && !!pet?.breed,
  });

  const { data: records = [] } = useQuery({
    queryKey: ['medical-records', id],
    queryFn: () => healthApi.records(Number(id)).then((r) => r.data.results || r.data),
    enabled: tab === 'health',
  });

  const { data: prescriptions = [] } = useQuery({
    queryKey: ['prescriptions', id],
    queryFn: () => healthApi.prescriptions(Number(id)).then((r) => r.data.results || r.data),
    enabled: tab === 'health',
  });

  const { data: feedingLogs = [] } = useQuery({
    queryKey: ['feeding-logs', id],
    queryFn: () => feedingApi.logs(Number(id)).then((r) => r.data.results || r.data),
    enabled: tab === 'feeding',
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-32 skeleton rounded-3xl" />
        <div className="h-64 skeleton rounded-3xl" />
      </div>
    );
  }

  if (!pet) {
    return <div className="text-center py-24 text-obsidian-500">Pet not found.</div>;
  }

  const statusStyle = {
    healthy:     'bg-green-50 text-green-700 border-green-200',
    overweight:  'bg-amber-50 text-amber-700 border-amber-200',
    underweight: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/pets" className="btn-ghost flex items-center gap-2 text-sm">
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div className="flex-1" />
        <Link href={`/pets/${id}/edit`} className="btn-secondary flex items-center gap-2 text-sm py-2">
          <Edit className="w-4 h-4" /> Edit
        </Link>
      </div>

      {/* Pet hero card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="zoaria-card"
      >
        <div className="flex items-center gap-6">
          <div className="w-24 h-24 rounded-3xl bg-sage-100 flex items-center justify-center text-5xl overflow-hidden">
            {pet.photo_url
              ? <img src={pet.photo_url} alt={pet.name} className="w-full h-full object-cover" />
              : AVATARS[pet.avatar_type] || '🐾'}
          </div>
          <div className="flex-1">
            <h1 className="font-display text-3xl font-bold text-obsidian-900">{pet.name}</h1>
            <p className="text-obsidian-500 mt-1">
              {pet.species_name}{pet.breed_name && ` · ${pet.breed_name}`}
            </p>
            <div className="flex flex-wrap gap-2 mt-3">
              {pet.gender && pet.gender !== 'unknown' && (
                <span className="badge bg-sage-100 text-sage-700 capitalize">{pet.gender}</span>
              )}
              {pet.sterilized && (
                <span className="badge bg-sage-100 text-sage-700">Sterilized</span>
              )}
              {pet.age && (
                <span className="badge bg-sage-100 text-sage-700">{pet.age} months</span>
              )}
              {pet.weight_status && (
                <span className={cn('badge border capitalize',
                  statusStyle[pet.weight_status as keyof typeof statusStyle])}>
                  {pet.weight_status}
                </span>
              )}
            </div>
          </div>
          {/* Quick stats */}
          <div className="hidden sm:grid grid-cols-2 gap-3">
            {pet.weight && (
              <div className="text-center p-3 bg-sage-50 rounded-2xl">
                <p className="text-xs text-obsidian-400">Weight</p>
                <p className="font-bold text-obsidian-900">{pet.weight}kg</p>
              </div>
            )}
            {pet.mer && (
              <div className="text-center p-3 bg-brand-50 rounded-2xl">
                <p className="text-xs text-brand-600">Daily kcal</p>
                <p className="font-bold text-brand-900">{pet.mer}</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto p-1 bg-sage-100 rounded-2xl w-fit">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition-all',
              tab === key ? 'bg-white text-brand-700 shadow-card' : 'text-obsidian-500 hover:text-obsidian-700'
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <motion.div key={tab} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        {/* ── Overview ── */}
        {tab === 'overview' && (
          <div className="grid sm:grid-cols-2 gap-4">
            {/* BMI Widget */}
            {bmiData && (
              <div className="zoaria-card flex flex-col items-center">
                <h3 className="font-semibold text-obsidian-900 mb-4">{t('pets.bmi')}</h3>
                <BMIIndicator
                  normalized={bmiData.bmi_normalized}
                  status={bmiData.weight_status}
                  weight={bmiData.weight}
                  minWeight={bmiData.breed_min}
                  maxWeight={bmiData.breed_max}
                />
              </div>
            )}

            {/* Stats */}
            <div className="zoaria-card space-y-3">
              <h3 className="font-semibold text-obsidian-900">Details</h3>
              {[
                { label: 'Activity Level', value: pet.activity_level },
                { label: 'Height', value: pet.height ? `${pet.height}cm` : '—' },
                { label: 'Chip Number', value: pet.chip_number || '—' },
                { label: 'RER', value: pet.rer ? `${pet.rer} kcal/day` : '—' },
                { label: 'Daily Calories', value: pet.mer ? `${pet.mer} kcal/day` : '—' },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm border-b border-sage-100 pb-2 last:border-0 last:pb-0">
                  <span className="text-obsidian-500">{label}</span>
                  <span className="font-medium text-obsidian-800 capitalize">{value}</span>
                </div>
              ))}
            </div>

            {/* Medical notes */}
            {pet.medical_notes && (
              <div className="zoaria-card sm:col-span-2">
                <h3 className="font-semibold text-obsidian-900 mb-2">Medical Notes</h3>
                <p className="text-obsidian-600 text-sm leading-relaxed">{pet.medical_notes}</p>
              </div>
            )}
          </div>
        )}

        {/* ── Health ── */}
        {tab === 'health' && (
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="zoaria-card">
              <h3 className="font-semibold text-obsidian-900 mb-4">Medical Records</h3>
              {records.length === 0
                ? <p className="text-obsidian-400 text-sm text-center py-4">No records yet</p>
                : records.map((r: any) => (
                    <div key={r.id} className="p-3 bg-sage-50 rounded-xl mb-2">
                      <p className="font-medium text-sm text-obsidian-800">{r.diagnosis || 'Visit'}</p>
                      <p className="text-xs text-obsidian-400 mt-1">{new Date(r.created_at).toLocaleDateString()}</p>
                      {r.treatment && <p className="text-xs text-obsidian-600 mt-1">{r.treatment}</p>}
                    </div>
                  ))
              }
            </div>
            <div className="zoaria-card">
              <h3 className="font-semibold text-obsidian-900 mb-4">Prescriptions</h3>
              {prescriptions.length === 0
                ? <p className="text-obsidian-400 text-sm text-center py-4">No prescriptions</p>
                : prescriptions.map((p: any) => (
                    <div key={p.id} className="p-3 bg-sage-50 rounded-xl mb-2">
                      <p className="font-semibold text-sm text-obsidian-800">{p.medication_name}</p>
                      <p className="text-xs text-obsidian-500">{p.dosage} · {p.duration}</p>
                    </div>
                  ))
              }
            </div>
          </div>
        )}

        {/* ── Feeding ── */}
        {tab === 'feeding' && (
          <div className="zoaria-card">
            <h3 className="font-semibold text-obsidian-900 mb-4">Feeding Log</h3>
            {feedingLogs.length === 0
              ? <p className="text-obsidian-400 text-sm text-center py-8">No feeding logs yet</p>
              : feedingLogs.map((f: any) => (
                  <div key={f.id} className="flex items-center gap-3 p-3 border-b border-sage-100">
                    <span className="text-2xl">🥗</span>
                    <div className="flex-1">
                      <p className="font-medium text-sm text-obsidian-800">{f.food_type}</p>
                      <p className="text-xs text-obsidian-400">{f.amount}g · {f.calories || '?'}kcal</p>
                    </div>
                    <p className="text-xs text-obsidian-400">{new Date(f.created_at).toLocaleDateString()}</p>
                  </div>
                ))
            }
          </div>
        )}

        {/* ── Activity / Calendar placeholders ── */}
        {(tab === 'activity' || tab === 'calendar') && (
          <div className="zoaria-card text-center py-12 border-dashed">
            <div className="text-4xl mb-3">{tab === 'activity' ? '🏃' : '📅'}</div>
            <h3 className="font-semibold text-obsidian-900 mb-1">
              {tab === 'activity' ? 'Activity Tracking' : 'Health Calendar'}
            </h3>
            <p className="text-obsidian-500 text-sm">Coming in Phase 4</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
