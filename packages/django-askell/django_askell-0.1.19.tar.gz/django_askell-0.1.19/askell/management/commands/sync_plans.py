from django.core.management.base import BaseCommand
from askell.client import client
from askell.models import Plan


class Command(BaseCommand):
    def handle(self, *args, **options):

        old_plans = Plan.objects.all()
        old_plans.update(enabled=False, private=True)

        plans = client.get_plans()

        for plan in plans:

            id = plan.pop('id')
            Plan.objects.update_or_create(plan_id=id, defaults=plan)
