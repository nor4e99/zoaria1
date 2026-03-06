from django.urls import path
from .views import SubscribeView, StripeWebhookView, MySubscriptionView, PaymentHistoryView

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('my-subscription/', MySubscriptionView.as_view(), name='my-subscription'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
]
