
# Create your models here.
from askell.models import Payment, Plan

from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.snippets.views.snippets import CreateView


class CustomModelPermissionPolicy(ModelPermissionPolicy):

    def user_has_permission(self, user, action):
        """
        Override the permission check in the create view.
        The permission policy is what prevents the action button from showing up in the admin.
        """
        if action == 'add':
            return False
        return super().user_has_permission(user, action)


class CustomCreateView(CreateView):

    def user_has_permission(self, permission):
        """
        Override the permission check in the create view.
        If this was done with a custom permission policy, the superuser would be able to add snippets.
        """
        if permission == 'add':
            return False
        return self.permission_policy.user_has_permission(self.request.user, permission)


class PaymentViewSet(SnippetViewSet):
    model = Payment
    add_view_class = CustomCreateView
    permission_policy = CustomModelPermissionPolicy(Payment)

    panels = [
        FieldPanel('description'),
        FieldPanel('amount'),
        FieldPanel('currency'),
    ]

register_snippet(PaymentViewSet)


class PlanViewSet(SnippetViewSet):
    model = Plan
    add_view_class = CustomCreateView
    permission_policy = CustomModelPermissionPolicy(Plan)

    panels = [
        FieldPanel('description'),
        FieldPanel('amount'),
        FieldPanel('currency'),
    ]

register_snippet(PlanViewSet)
