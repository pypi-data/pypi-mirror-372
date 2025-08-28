from django.contrib import admin

from .models import Payment, Plan


class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ('reference', 'created_at', 'state', 'amount', 'currency')
    list_filter = ('state', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PlanAdmin(admin.ModelAdmin):
    model = Plan
    list_display = ('name', 'amount', 'currency', 'enabled')
    list_filter = ('enabled', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Plan, PlanAdmin)
