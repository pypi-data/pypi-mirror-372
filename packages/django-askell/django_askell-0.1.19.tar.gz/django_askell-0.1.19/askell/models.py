import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from .webhooks import register_webhook_handler
from .webhook_handlers import payment_created, payment_changed

user_model = get_user_model()


class Payment(models.Model):

    class STATES(object):
        PENDING = 'pending'
        SETTLED = 'settled'
        FAILED = 'failed'
        RETRYING = 'retrying'
        REFUNDED = 'refunded'

    STATE_CHOICES = (
        (STATES.PENDING, _('Pending')),
        (STATES.SETTLED, _('Settled')),
        (STATES.FAILED, _('Failed')),
        (STATES.RETRYING, _('Retrying')),
        (STATES.REFUNDED, _('Refunded')),
    )


    KEYS_TO_COPY = ['description', 'reference', 'amount', 'currency']

    uuid = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    description = models.CharField(max_length=1024, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    state= models.CharField(max_length=20, choices=STATE_CHOICES, default=STATES.PENDING)
    reference = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(user_model, blank=True, null=True, on_delete=models.SET_NULL, related_name='payments')

    def as_dict(self):
        return {
            'uuid': self.uuid,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'state': self.state,
            'reference': self.reference,
            'amount': self.amount,
            'currency': self.currency,
            'user': self.user.id if self.user else None,
        }

register_webhook_handler(payment_created)
register_webhook_handler(payment_changed)

# @register_snippet
# class Subscription(models.Model):
#     user = models.ForeignKey('auth.User', blank=True, null=True, on_delete=models.SET_NULL, related_name='subscriptions')
#     reference = models.CharField(max_length=255)
#     active_until = models.DateTimeField(blank=True, null=True)
#     token = models.CharField(max_length=100, blank=True)
#     active = models.BooleanField(default=False)
#     is_on_trial = models.BooleanField(default=False)
#     plan = models.ForeignKey('askell.Plan', to_field='plan_id', on_delete=models.CASCADE, null=True, blank=True)
#     description = models.CharField(max_length=1024, blank=True, null=True)
#     subscription_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    
#     def __str__(self):
#         if self.user:
#             return f"Subscription for {self.user.username} ({self.user.id})"
#         else:
#             return f"Subscription for {self.reference} (no user linked)"

#     panels = [
#         FieldPanel('user'),
#         FieldPanel('reference'),
#         FieldPanel('active_until'),
#         FieldPanel('token'),
#         FieldPanel('active'),
#         FieldPanel('is_on_trial'),
#         FieldPanel('plan'),
#         FieldPanel('description'),
#         FieldPanel('subscription_id'),
#     ]


class Plan(models.Model):
    plan_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=512)
    alternative_name = models.CharField(max_length=512, blank=True, null=True)
    reference = models.CharField(max_length=512, blank=True, null=True)
    interval = models.CharField(max_length=50, blank=True, null=True)
    interval_count = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    trial_period_days = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    electronic_only = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# @register_snippet
# class PlanGroups(models.Model):

#     plan = ParentalKey(Plan, related_name='groups', on_delete=models.CASCADE)
#     group = models.ForeignKey(Group, on_delete=models.CASCADE)

#     panels = [
#          MultiFieldPanel(
#             [
#                 FieldPanel("plan"),
#                 FieldPanel("group"),
#             ],
#             heading="Plan / Group relations",
#         ),
#     ]

#     def __str__(self):
#         return f"{self.plan.name} -> {self.group.name}"

