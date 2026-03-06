from django.urls import path
from .views import (
    PetListCreateView,
    PetDetailView,
    PetBMIView,
    SpeciesListView,
    BreedListView,
    BreedDetailView,
    BreedConditionsView,
)

urlpatterns = [
    # Pet CRUD
    path('', PetListCreateView.as_view(), name='pet-list-create'),
    path('<int:pk>/', PetDetailView.as_view(), name='pet-detail'),
    path('<int:pk>/bmi/', PetBMIView.as_view(), name='pet-bmi'),

    # Veterinary reference data
    path('species/', SpeciesListView.as_view(), name='species-list'),
    path('breeds/', BreedListView.as_view(), name='breed-list'),
    path('breeds/<int:pk>/', BreedDetailView.as_view(), name='breed-detail'),
    path('breeds/<int:breed_id>/conditions/', BreedConditionsView.as_view(), name='breed-conditions'),
]
