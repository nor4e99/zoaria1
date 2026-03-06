from rest_framework import serializers
from .models import Pet, Species, Breed, BreedCondition


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name']


class BreedConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedCondition
        fields = ['id', 'condition_name']


class BreedSerializer(serializers.ModelSerializer):
    conditions = BreedConditionSerializer(many=True, read_only=True)

    class Meta:
        model = Breed
        fields = ['id', 'breed_name', 'min_weight', 'max_weight', 'conditions']


class BreedListSerializer(serializers.ModelSerializer):
    """Lightweight list without conditions."""
    class Meta:
        model = Breed
        fields = ['id', 'breed_name', 'min_weight', 'max_weight']


class PetSerializer(serializers.ModelSerializer):
    species_name = serializers.CharField(source='species.name', read_only=True)
    breed_name = serializers.CharField(source='breed.breed_name', read_only=True)
    weight_status = serializers.ReadOnlyField()
    bmi_normalized = serializers.ReadOnlyField()
    rer = serializers.ReadOnlyField()
    mer = serializers.ReadOnlyField()

    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'species', 'species_name', 'breed', 'breed_name',
            'gender', 'sterilized', 'age', 'weight', 'ideal_weight', 'height',
            'activity_level', 'chip_number', 'medical_notes', 'avatar_type',
            'photo_url', 'created_at',
            # computed
            'weight_status', 'bmi_normalized', 'rer', 'mer',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        # Check breed belongs to species if both provided
        species = attrs.get('species')
        breed = attrs.get('breed')
        if breed and species and breed.species != species:
            raise serializers.ValidationError({'breed': 'Breed does not belong to the selected species.'})
        return attrs

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class PetListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""
    species_name = serializers.CharField(source='species.name', read_only=True)
    breed_name = serializers.CharField(source='breed.breed_name', read_only=True)
    weight_status = serializers.ReadOnlyField()

    class Meta:
        model = Pet
        fields = ['id', 'name', 'species', 'species_name', 'breed_name',
                  'age', 'weight', 'weight_status', 'avatar_type', 'photo_url']
