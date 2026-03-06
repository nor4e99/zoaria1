from rest_framework.permissions import BasePermission


class SubscriptionPermission(BasePermission):
    """
    Generic subscription gate.
    Set `required_plan` on the view to enforce plan level.
    Plans in order: basic < standard < premium
    """
    PLAN_LEVELS = {'basic': 0, 'standard': 1, 'premium': 2}

    def has_permission(self, request, view):
        required_plan = getattr(view, 'required_plan', 'basic')
        required_level = self.PLAN_LEVELS.get(required_plan, 0)

        try:
            from apps.payments.models import Subscription
            sub = Subscription.objects.filter(
                user=request.user, active=True
            ).order_by('-start_date').first()
            user_plan = sub.plan_name if sub else 'basic'
        except Exception:
            user_plan = 'basic'

        user_level = self.PLAN_LEVELS.get(user_plan, 0)
        return user_level >= required_level
