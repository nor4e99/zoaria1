from django.urls import path
from .views import FeedingLogView, FeedingGuidelinesView, CalorieCalculatorView

urlpatterns = [
    path('pets/<int:pet_id>/logs/', FeedingLogView.as_view(), name='feeding-log'),
    path('pets/<int:pet_id>/calories/', CalorieCalculatorView.as_view(), name='calorie-calculator'),
    path('guidelines/<int:species_id>/', FeedingGuidelinesView.as_view(), name='feeding-guidelines'),
]
