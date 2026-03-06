import { PetCreateForm } from '@/components/pets/PetCreateForm';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function NewPetPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <Link href="/pets" className="btn-ghost flex items-center gap-2 text-sm">
          <ArrowLeft className="w-4 h-4" /> Back to Pets
        </Link>
        <div>
          <h1 className="font-display text-2xl font-bold text-obsidian-900">Add New Pet</h1>
          <p className="text-obsidian-500 text-sm mt-1">Create a health profile for your pet</p>
        </div>
      </div>
      <PetCreateForm />
    </div>
  );
}
