from django.urls import path
from .views import PetMedicalRecordView, PetPrescriptionView

urlpatterns = [
    path('pets/<int:pet_id>/records/', PetMedicalRecordView.as_view(), name='pet-medical-records'),
    path('pets/<int:pet_id>/prescriptions/', PetPrescriptionView.as_view(), name='pet-prescriptions'),
]
