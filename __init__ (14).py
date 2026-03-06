"""
Management command to seed the veterinary reference data from zoaria_veterinary_database.sql
Run with: python manage.py seed_db
"""
from django.core.management.base import BaseCommand
from apps.pets.models import Species, Breed, BreedCondition
from apps.feeding.models import FeedingGuideline
from apps.calendar_app.models import Reminder  # just to ensure migrations are applied


SPECIES_DATA = [
    (1, 'Dog'), (2, 'Cat'), (3, 'Horse'),
    (4, 'Rabbit'), (5, 'Guinea Pig'), (6, 'Bird'), (7, 'Exotic'),
]

BREEDS_DATA = [
    # Dogs
    (1, 'Labrador Retriever', 13.47, 43.18),
    (1, 'German Shepherd', 10.69, 52.49),
    (1, 'Golden Retriever', 14.06, 49.7),
    (1, 'Bulldog', 13.99, 50.3),
    (1, 'Poodle', 10.72, 53.7),
    (1, 'Beagle', 14.36, 46.87),
    (1, 'Rottweiler', 12.55, 39.37),
    (1, 'Doberman', 15.45, 55.68),
    (1, 'Boxer', 15.37, 37.84),
    (1, 'Chihuahua', 13.9, 41.22),
    (1, 'Husky', 16.03, 55.28),
    (1, 'Great Dane', 13.64, 48.31),
    (1, 'Mastiff', 15.3, 52.13),
    (1, 'Border Collie', 11.62, 45.89),
    (1, 'Cocker Spaniel', 14.09, 43.76),
    (1, 'Dachshund', 16.38, 36.17),
    (1, 'Shiba Inu', 13.41, 46.43),
    (1, 'Akita', 10.91, 51.51),
    (1, 'Alaskan Malamute', 13.88, 40.44),
    (1, 'Dalmatian', 11.09, 51.84),
    (1, 'Newfoundland', 11.66, 54.34),
    (1, 'Cane Corso', 14.87, 37.31),
    # Cats
    (2, 'Maine Coon', 2.85, 13.31),
    (2, 'Persian', 2.79, 13.2),
    (2, 'Siamese', 2.91, 9.37),
    (2, 'Bengal', 2.14, 12.26),
    (2, 'Ragdoll', 3.18, 12.85),
    (2, 'British Shorthair', 2.36, 13.72),
    (2, 'Sphynx', 2.29, 10.78),
    (2, 'Scottish Fold', 2.77, 13.61),
    (2, 'Abyssinian', 2.31, 9.65),
    (2, 'Birman', 2.62, 11.92),
    (2, 'Oriental Shorthair', 2.27, 11.33),
    (2, 'Savannah', 2.18, 9.9),
    (2, 'Devon Rex', 2.39, 10.41),
    (2, 'Cornish Rex', 3.13, 11.2),
    (2, 'Norwegian Forest Cat', 2.78, 9.73),
    # Horses
    (3, 'Arabian Horse', 269.51, 711.23),
    (3, 'Thoroughbred', 314.93, 792.02),
    (3, 'Quarter Horse', 363.54, 687.41),
    (3, 'Clydesdale', 344.59, 758.26),
    (3, 'Appaloosa', 280.99, 863.75),
    (3, 'Mustang', 380.95, 817.8),
    (3, 'Morgan', 303.33, 647.14),
    (3, 'Andalusian', 411.24, 860.18),
    (3, 'Friesian', 368.89, 730.31),
    (3, 'Paint Horse', 360.95, 782.43),
    # Rabbits
    (4, 'Holland Lop', 0.73, 11.01),
    (4, 'Flemish Giant', 1.05, 9.05),
    (4, 'Netherland Dwarf', 0.86, 13.38),
    (4, 'Mini Rex', 0.95, 10.9),
    (4, 'Lionhead', 0.91, 9.44),
    # Guinea Pigs
    (5, 'American Guinea Pig', 0.61, 2.02),
    (5, 'Peruvian Guinea Pig', 0.63, 1.88),
    (5, 'Abyssinian Guinea Pig', 0.76, 1.84),
    # Birds
    (6, 'Parrot', 0.04, 2.55),
    (6, 'Cockatiel', 0.05, 2.25),
    (6, 'Canary', 0.05, 1.9),
    (6, 'Budgerigar', 0.05, 2.49),
]

FEEDING_GUIDELINES = [
    (1, 'Food Type', 'Dry Food'),
    (1, 'Food Type', 'Wet Food'),
    (1, 'Food Type', 'BARF'),
    (1, 'Food Type', 'Mixed'),
    (1, 'Food Type', 'Veterinary Diet'),
    (2, 'Food Type', 'Wet Food'),
    (2, 'Food Type', 'Dry Food'),
    (2, 'Food Type', 'BARF'),
    (2, 'Food Type', 'Mixed'),
    (2, 'Food Type', 'Veterinary Diet'),
    (3, 'Concentrate', 'Oats'),
    (3, 'Concentrate', 'Muesli'),
    (3, 'Concentrate', 'Corn'),
    (3, 'Concentrate', 'Barley'),
    (3, 'Roughage', 'Hay'),
    (3, 'Roughage', 'Alfalfa'),
    (4, 'Recommended', 'Hay (constant)'),
    (4, 'Recommended', 'Pellets'),
    (4, 'Recommended', 'Fresh Vegetables'),
    (5, 'Recommended', 'Pellets'),
    (5, 'Recommended', 'Fresh Vegetables'),
    (5, 'Recommended', 'Hay'),
    (5, 'Warning', 'Vitamin C required daily'),
    (6, 'Recommended', 'Seeds'),
    (6, 'Recommended', 'Pellets'),
    (6, 'Recommended', 'Fresh Fruits'),
]


class Command(BaseCommand):
    help = 'Seed veterinary reference data into the database'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding ZOARIA database...')

        # Species
        for pk, name in SPECIES_DATA:
            Species.objects.update_or_create(id=pk, defaults={'name': name})
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(SPECIES_DATA)} species'))

        # Breeds
        count = 0
        for species_id, breed_name, min_w, max_w in BREEDS_DATA:
            Breed.objects.get_or_create(
                species_id=species_id,
                breed_name=breed_name,
                defaults={'min_weight': min_w, 'max_weight': max_w},
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} breeds'))

        # Breed conditions - map to Labrador (first dog breed)
        labrador = Breed.objects.filter(breed_name='Labrador Retriever').first()
        if labrador:
            conditions = [
                'Hip dysplasia', 'Elbow dysplasia', 'Progressive retinal atrophy',
                'Exercise-induced collapse', 'Obesity tendency',
            ]
            for c in conditions:
                BreedCondition.objects.get_or_create(breed=labrador, condition_name=c)

        german = Breed.objects.filter(breed_name='German Shepherd').first()
        if german:
            for c in ['Hip dysplasia', 'Degenerative myelopathy', 'Bloat (GDV)']:
                BreedCondition.objects.get_or_create(breed=german, condition_name=c)

        maine_coon = Breed.objects.filter(breed_name='Maine Coon').first()
        if maine_coon:
            for c in ['Hypertrophic cardiomyopathy', 'Hip dysplasia', 'Spinal muscular atrophy']:
                BreedCondition.objects.get_or_create(breed=maine_coon, condition_name=c)

        self.stdout.write(self.style.SUCCESS('  ✓ Breed conditions'))

        # Feeding guidelines
        FeedingGuideline.objects.all().delete()
        for species_id, category, food_name in FEEDING_GUIDELINES:
            FeedingGuideline.objects.create(
                species_id=species_id,
                food_category=category,
                food_name=food_name,
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(FEEDING_GUIDELINES)} feeding guidelines'))

        self.stdout.write(self.style.SUCCESS('\n🐾 ZOARIA database seeded successfully!'))
