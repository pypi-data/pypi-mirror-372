from django.urls import path

from .views import (
    CustomerView,
    CheckoutView,
    PaymentView,
    PaymentMethodView,
    TransactionReceiptView,
    UpdateCardView,
    WebhookHandlerView
)


urls = [
    path('customer/', CustomerView.as_view(), name='customer'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment/<uuid:uuid>/', PaymentView.as_view(), name='payment-detail'),
    path('payment_method/', PaymentMethodView.as_view(), name='payment-method'),
    path('transactions/<uuid:uuid>/receipt/', TransactionReceiptView.as_view(), name='transaction-receipt'),
    path('updatecard/', UpdateCardView.as_view(), name='update-card'),
    path('webhook/', WebhookHandlerView.as_view(), name='webhook'),
]
