'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { petsApi, feedingApi } from '@/lib/api';
import { BMIIndicator } from './BMIIndicator';
import { useT } from '@/hooks/useTranslation';
import { toast } from '@/components/ui/Toaster';
import { cn } from '@/lib/utils';
import { ArrowRight, ArrowLeft, AlertTriangle, Info, Loader2 } from 'lucide-react';

const schema = z.object({
  name: z.string().min(1, 'Name required'),
  species: z.number({ required_error: 'Select a species' }),
  breed: z.number().optional(),
  gender: z.enum(['male', 'female', 'unknown']).default('unknown'),
  sterilized: z.boolean().default(false),
  age: z.coerce.number().min(0).optional(),
  weight: z.coerce.number().min(0.01).optional(),
  ideal_weight: z.coerce.number().optional(),
  height: z.coerce.number().optional(),
  activity_level: z.enum(['low', 'moderate', 'active', 'very_active']).default('moderate'),
  chip_number: z.string().optional(),
  medical_notes: z.string().optional(),
  avatar_type: z.string().optional(),
});
type FormData = z.infer<typeof schema>;

const AVATARS = [
  { key: 'dog',     emoji: '🐕', label: 'Dog' },
  { key: 'cat',     emoji: '🐈', label: 'Cat' },
  { key: 'horse',   emoji: '🐎', label: 'Horse' },
  { key: 'rabbit',  emoji: '🐇', label: 'Rabbit' },
  { key: 'guinea',  emoji: '🐹', label: 'Guinea Pig' },
  { key: 'bird',    emoji: '🦜', label: 'Bird' },
  { key: 'fish',    emoji: '🐠', label: 'Fish' },
  { key: 'turtle',  emoji: '🐢', label: 'Turtle' },
];

const STEPS = ['Basic Info', 'Health & Weight', 'Feeding & Activity'];

export function PetCreateForm() {
  const t = useT();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, watch, setValue, control, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { gender: 'unknown', activity_level: 'moderate', sterilized: false },
  });

  const selectedSpecies = watch('species');
  const selectedBreed = watch('breed');
  const weight = watch('weight');
  const avatarType = watch('avatar_type');

  // Load species
  const { data: speciesData } = useQuery({
    queryKey: ['species'],
    queryFn: () => petsApi.species().then((r) => r.data),
  });

  // Load breeds when species selected
  const { data: breedsData, isLoading: breedsLoading } = useQuery({
    queryKey: ['breeds', selectedSpecies],
    queryFn: () => petsApi.breeds(selectedSpecies).then((r) => r.data),
    enabled: !!selectedSpecies,
  });

  // Load breed conditions
  const { data: conditions } = useQuery({
    queryKey: ['conditions', selectedBreed],
    queryFn: () => petsApi.breedConditions(selectedBreed!).then((r) => r.data),
    enabled: !!selectedBreed,
  });

  // Load feeding guidelines
  const { data: feedingData } = useQuery({
    queryKey: ['feeding', selectedSpecies],
    queryFn: () => feedingApi.guidelines(selectedSpecies).then((r) => r.data),
    enabled: !!selectedSpecies,
  });

  // Find breed reference weights for BMI
  const selectedBreedData = breedsData?.find((b: any) => b.id === selectedBreed);
  const bmiNormalized = selectedBreedData && weight
    ? Math.max(0, Math.min(1,
        (weight - (selectedBreedData.min_weight + selectedBreedData.max_weight) / 2 - (selectedBreedData.max_weight - selectedBreedData.min_weight) * 0.75) /
        ((selectedBreedData.max_weight - selectedBreedData.min_weight) * 1.5)
      ))
    : null;

  const weightStatus = selectedBreedData && weight
    ? weight < selectedBreedData.min_weight ? 'underweight'
      : weight > selectedBreedData.max_weight ? 'overweight'
      : 'healthy'
    : null;

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    try {
      await petsApi.create(data);
      toast.success('Pet profile created!');
      router.push('/pets');
    } catch (err: any) {
      const msg = err.response?.data?.detail || Object.values(err.response?.data || {})[0] || 'Failed to create pet';
      toast.error(String(msg));
    } finally {
      setIsSubmitting(false);
    }
  };

  // Reset breed when species changes
  useEffect(() => {
    setValue('breed', undefined);
  }, [selectedSpecies]);

  const isGuineaPig = speciesData?.find((s: any) => s.id === selectedSpecies)?.name === 'Guinea Pig';

  return (
    <div className="max-w-2xl mx-auto">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2 flex-1">
            <div className={cn(
              'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all',
              i < step ? 'bg-brand-500 text-white' :
              i === step ? 'bg-brand-500 text-white ring-4 ring-brand-100' :
              'bg-sage-200 text-obsidian-400'
            )}>
              {i < step ? '✓' : i + 1}
            </div>
            <span className={cn('text-sm font-medium hidden sm:block',
              i === step ? 'text-brand-700' : 'text-obsidian-400')}>{s}</span>
            {i < STEPS.length - 1 && (
              <div className={cn('flex-1 h-0.5 rounded', i < step ? 'bg-brand-400' : 'bg-sage-200')} />
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <AnimatePresence mode="wait">
          {/* ── STEP 0: Basic Info ── */}
          {step === 0 && (
            <motion.div key="step0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
              className="space-y-5">
              <div>
                <label className="label-base">{t('pets.name')} *</label>
                <input {...register('name')} className={cn('input-base', errors.name && 'border-red-400')}
                  placeholder="Buddy, Luna, Mochi..." />
                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
              </div>

              {/* Avatar selector */}
              <div>
                <label className="label-base">Avatar</label>
                <div className="flex flex-wrap gap-2">
                  {AVATARS.map((a) => (
                    <button key={a.key} type="button"
                      onClick={() => setValue('avatar_type', a.key)}
                      className={cn(
                        'flex flex-col items-center gap-1 p-3 rounded-2xl border-2 transition-all text-center w-16',
                        avatarType === a.key
                          ? 'border-brand-400 bg-brand-50'
                          : 'border-sage-200 hover:border-sage-300 bg-white'
                      )}>
                      <span className="text-2xl">{a.emoji}</span>
                      <span className="text-xs text-obsidian-500">{a.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Species */}
              <div>
                <label className="label-base">{t('pets.species')} *</label>
                <select {...register('species', { valueAsNumber: true })}
                  className={cn('input-base', errors.species && 'border-red-400')}>
                  <option value="">{t('pets.selectSpecies')}</option>
                  {speciesData?.map((s: any) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
                {errors.species && <p className="text-red-500 text-xs mt-1">{errors.species.message}</p>}
              </div>

              {/* Breed - appears after species selected */}
              {selectedSpecies && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                  <label className="label-base">{t('pets.breed')}</label>
                  <select {...register('breed', { valueAsNumber: true })}
                    className="input-base" disabled={breedsLoading}>
                    <option value="">{breedsLoading ? 'Loading...' : t('pets.selectBreed')}</option>
                    {breedsData?.map((b: any) => (
                      <option key={b.id} value={b.id}>{b.breed_name}</option>
                    ))}
                  </select>

                  {/* Breed health risk chips */}
                  {conditions && conditions.length > 0 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      className="mt-3 p-3 bg-amber-50 rounded-2xl border border-amber-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4 text-amber-600" />
                        <span className="text-xs font-semibold text-amber-700">{t('pets.conditions')}</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {conditions.map((c: any) => (
                          <span key={c.id} className="badge bg-white border border-amber-300 text-amber-700">
                            {c.condition_name}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )}

              {/* Gender & age in a row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label-base">{t('pets.gender')}</label>
                  <select {...register('gender')} className="input-base">
                    <option value="unknown">{t('pets.unknown')}</option>
                    <option value="male">{t('pets.male')}</option>
                    <option value="female">{t('pets.female')}</option>
                  </select>
                </div>
                <div>
                  <label className="label-base">{t('pets.age')}</label>
                  <input {...register('age')} type="number" min="0" className="input-base" placeholder="12" />
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 bg-sage-50 rounded-2xl border border-sage-200">
                <input {...register('sterilized')} type="checkbox" id="sterilized"
                  className="w-5 h-5 rounded border-sage-300 text-brand-500 focus:ring-brand-400" />
                <label htmlFor="sterilized" className="text-sm font-medium text-obsidian-700">
                  {t('pets.sterilized')}
                </label>
              </div>
            </motion.div>
          )}

          {/* ── STEP 1: Health & Weight ── */}
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
              className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label-base">{t('pets.weight')} *</label>
                  <input {...register('weight')} type="number" step="0.1" min="0"
                    className="input-base" placeholder="4.5" />
                </div>
                <div>
                  <label className="label-base">{t('pets.idealWeight')}</label>
                  <input {...register('ideal_weight')} type="number" step="0.1" min="0"
                    className="input-base" placeholder="5.0" />
                </div>
              </div>
              <div>
                <label className="label-base">{t('pets.height')}</label>
                <input {...register('height')} type="number" step="0.5" min="0"
                  className="input-base" placeholder="60" />
              </div>

              {/* BMI Indicator - appears when breed + weight available */}
              {selectedBreedData && weight && bmiNormalized !== null && (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="flex flex-col items-center py-4 bg-white rounded-3xl border border-sage-200"
                >
                  <p className="text-sm font-semibold text-obsidian-600 mb-2">{t('pets.bmi')}</p>
                  <BMIIndicator
                    normalized={bmiNormalized}
                    status={weightStatus as any}
                    weight={weight}
                    minWeight={selectedBreedData.min_weight}
                    maxWeight={selectedBreedData.max_weight}
                  />
                  <div className="mt-3 grid grid-cols-2 gap-4 text-center text-sm">
                    <div className="p-3 bg-sage-50 rounded-2xl">
                      <p className="text-obsidian-400 text-xs">{t('pets.rer')}</p>
                      <p className="font-bold text-obsidian-900">
                        {Math.round(70 * Math.pow(weight, 0.75))} kcal
                      </p>
                    </div>
                    <div className="p-3 bg-sage-50 rounded-2xl">
                      <p className="text-obsidian-400 text-xs">{t('pets.mer')}</p>
                      <p className="font-bold text-obsidian-900">
                        {Math.round(70 * Math.pow(weight, 0.75) * 1.4)} kcal
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              <div>
                <label className="label-base">{t('pets.chipNumber')}</label>
                <input {...register('chip_number')} className="input-base" placeholder="985112345678901" />
              </div>
              <div>
                <label className="label-base">{t('pets.medicalNotes')}</label>
                <textarea {...register('medical_notes')} rows={3}
                  className="input-base resize-none" placeholder="Any chronic conditions, allergies..." />
              </div>
            </motion.div>
          )}

          {/* ── STEP 2: Feeding & Activity ── */}
          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
              className="space-y-5">
              {/* Activity level */}
              <div>
                <label className="label-base">{t('pets.activityLevel')}</label>
                <div className="grid grid-cols-2 gap-2">
                  {([
                    { value: 'low', label: t('pets.low'), emoji: '🛋️' },
                    { value: 'moderate', label: t('pets.moderate'), emoji: '🚶' },
                    { value: 'active', label: t('pets.active'), emoji: '🏃' },
                    { value: 'very_active', label: t('pets.veryActive'), emoji: '⚡' },
                  ] as const).map((opt) => (
                    <label key={opt.value}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-2xl border-2 cursor-pointer transition-all',
                        watch('activity_level') === opt.value
                          ? 'border-brand-400 bg-brand-50'
                          : 'border-sage-200 hover:border-sage-300 bg-white'
                      )}>
                      <input {...register('activity_level')} type="radio" value={opt.value} className="sr-only" />
                      <span className="text-xl">{opt.emoji}</span>
                      <span className="text-sm font-medium text-obsidian-700">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Vitamin C warning for Guinea Pig */}
              {isGuineaPig && (
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="p-4 bg-amber-50 rounded-2xl border-2 border-amber-300 flex gap-3"
                >
                  <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  <p className="text-sm text-amber-800">{t('pets.vitaminCWarning')}</p>
                </motion.div>
              )}

              {/* Feeding guidelines for this species */}
              {feedingData?.guidelines && feedingData.guidelines.length > 0 && (
                <div>
                  <label className="label-base">Feeding Options for this species</label>
                  <div className="grid grid-cols-2 gap-2">
                    {feedingData.guidelines.map((g: any) => (
                      <div key={g.id}
                        className="flex items-center gap-2 p-3 bg-sage-50 rounded-xl border border-sage-200 text-sm text-obsidian-700">
                        <span className="w-2 h-2 rounded-full bg-brand-400 shrink-0" />
                        <span>{g.food_name}</span>
                        <span className="text-xs text-obsidian-400 ml-auto">{g.food_category}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Calorie info preview */}
              {weight && (
                <div className="p-4 bg-brand-50 rounded-2xl border border-brand-200">
                  <p className="text-sm font-semibold text-brand-800 mb-2">📊 Estimated Daily Calories</p>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-brand-600">RER (Resting)</p>
                      <p className="font-bold text-obsidian-900">{Math.round(70 * Math.pow(weight, 0.75))} kcal</p>
                    </div>
                    <div>
                      <p className="text-brand-600">MER (Active)</p>
                      <p className="font-bold text-obsidian-900">
                        {Math.round(70 * Math.pow(weight, 0.75) * 1.4)} kcal
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-brand-500 mt-2">Formula: RER = 70 × weight^0.75</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex gap-3 mt-8">
          {step > 0 && (
            <button type="button" onClick={() => setStep(step - 1)} className="btn-secondary flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          )}
          {step < STEPS.length - 1 ? (
            <button type="button" onClick={() => setStep(step + 1)} className="btn-primary flex items-center gap-2 ml-auto">
              Continue <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2 ml-auto">
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              Create Pet Profile
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
