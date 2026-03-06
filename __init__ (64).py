from django.urls import path
from .views import PetPhotoUploadView, VetLicenseUploadView, GenericImageUploadView

urlpatterns = [
    path('pet-photo/',   PetPhotoUploadView.as_view(),   name='upload-pet-photo'),
    path('vet-license/', VetLicenseUploadView.as_view(), name='upload-vet-license'),
    path('image/',       GenericImageUploadView.as_view(), name='upload-image'),
]
