"""
ZOARIA Uploads — Cloudinary integration
  POST /api/uploads/pet-photo/    multipart: file, pet_id (optional)
  POST /api/uploads/vet-license/  multipart: file (PDF/image)
  POST /api/uploads/image/        multipart: file (generic chat attachment)
"""
import cloudinary
import cloudinary.uploader
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def _init():
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)


ALLOWED_IMAGES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
ALLOWED_DOCS   = {'application/pdf', 'image/jpeg', 'image/png', 'image/webp'}
MB = 1024 * 1024


class PetPhotoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        _init()
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file provided.'}, status=400)
        if f.content_type not in ALLOWED_IMAGES:
            return Response({'error': 'Use JPEG, PNG, or WebP.'}, status=400)
        if f.size > 5 * MB:
            return Response({'error': 'Max 5 MB.'}, status=400)
        try:
            result = cloudinary.uploader.upload(
                f, folder='zoaria/pets',
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'fill', 'gravity': 'face'},
                    {'quality': 'auto', 'fetch_format': 'auto'},
                ],
                resource_type='image',
            )
            photo_url = result['secure_url']
            pet_id = request.data.get('pet_id')
            if pet_id:
                from apps.pets.models import Pet
                try:
                    pet = Pet.objects.get(id=int(pet_id), owner=request.user)
                    pet.photo_url = photo_url
                    pet.save(update_fields=['photo_url'])
                except (Pet.DoesNotExist, ValueError):
                    pass
            return Response({'photo_url': photo_url, 'public_id': result['public_id']})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class VetLicenseUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if request.user.role != 'vet':
            return Response({'error': 'Only veterinarians can upload licenses.'}, status=403)
        _init()
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file provided.'}, status=400)
        if f.content_type not in ALLOWED_DOCS:
            return Response({'error': 'Use PDF, JPEG, or PNG.'}, status=400)
        if f.size > 10 * MB:
            return Response({'error': 'Max 10 MB.'}, status=400)
        try:
            rtype = 'raw' if f.content_type == 'application/pdf' else 'image'
            result = cloudinary.uploader.upload(
                f, folder='zoaria/vet_licenses',
                resource_type=rtype,
                use_filename=True, unique_filename=True,
            )
            doc_url = result['secure_url']
            from apps.vets.models import VetProfile
            try:
                vp = VetProfile.objects.get(user=request.user)
                vp.license_document = doc_url
                vp.save(update_fields=['license_document'])
            except VetProfile.DoesNotExist:
                pass
            return Response({'document_url': doc_url, 'public_id': result['public_id']})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GenericImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        _init()
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'No file provided.'}, status=400)
        if f.size > 10 * MB:
            return Response({'error': 'Max 10 MB.'}, status=400)
        try:
            is_pdf = f.content_type == 'application/pdf'
            result = cloudinary.uploader.upload(
                f, folder='zoaria/attachments',
                resource_type='raw' if is_pdf else 'auto',
            )
            return Response({'url': result['secure_url'], 'public_id': result['public_id']})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
