import stripe
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription, Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICES = {
    'basic': None,      # Free
    'standard': 9.99,
    'premium': 19.99,
}


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = request.data.get('plan')
        if plan not in PLAN_PRICES:
            return Response({'error': 'Invalid plan.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Deactivate old subscriptions
        Subscription.objects.filter(user=user, active=True).update(active=False)

        if plan == 'basic':
            Subscription.objects.create(
                user=user,
                plan_name='basic',
                start_date=date.today(),
                active=True,
            )
            return Response({'message': 'Switched to Basic plan.', 'plan': 'basic'})

        # Create Stripe checkout session
        price_id = settings.STRIPE_PLANS.get(plan)
        if not price_id:
            return Response({'error': 'Stripe price not configured.'}, status=500)

        try:
            session = stripe.checkout.Session.create(
                mode='subscription',
                payment_method_types=['card'],
                customer_email=user.email,
                line_items=[{'price': price_id, 'quantity': 1}],
                success_url=f"{settings.FRONTEND_URL}/dashboard?subscribed=1",
                cancel_url=f"{settings.FRONTEND_URL}/pricing",
                metadata={'user_id': user.id, 'plan': plan},
            )
            return Response({'checkout_url': session.url})
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=500)


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata'].get('user_id')
            plan = session['metadata'].get('plan')
            amount = session.get('amount_total', 0) / 100

            if user_id and plan:
                from apps.users.models import User
                try:
                    user = User.objects.get(id=user_id)
                    Subscription.objects.filter(user=user, active=True).update(active=False)
                    Subscription.objects.create(
                        user=user,
                        plan_name=plan,
                        start_date=date.today(),
                        end_date=date.today() + timedelta(days=30),
                        active=True,
                        stripe_subscription_id=session.get('subscription', ''),
                    )
                    Payment.objects.create(
                        user=user,
                        amount=amount,
                        currency='EUR',
                        payment_status='succeeded',
                        stripe_payment_intent_id=session.get('payment_intent', ''),
                    )
                except User.DoesNotExist:
                    pass

        elif event['type'] == 'customer.subscription.deleted':
            stripe_sub_id = event['data']['object']['id']
            Subscription.objects.filter(
                stripe_subscription_id=stripe_sub_id
            ).update(active=False)

        return Response({'status': 'ok'})


class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sub = Subscription.objects.filter(
            user=request.user, active=True
        ).order_by('-start_date').first()

        if sub:
            return Response({
                'plan': sub.plan_name,
                'start_date': sub.start_date,
                'end_date': sub.end_date,
                'active': sub.active,
            })
        return Response({'plan': 'basic', 'active': True})


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:20]
        data = [
            {
                'id': p.id,
                'amount': str(p.amount),
                'currency': p.currency,
                'status': p.payment_status,
                'date': p.created_at,
            }
            for p in payments
        ]
        return Response(data)
