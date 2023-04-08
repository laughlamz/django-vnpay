from django.urls import path

from vnpay.api.payment_ipn import VnPayPaymentIpnApi
from vnpay.api.payment_return import VnPayPaymentReturnApi
from vnpay.api.payment_url import VnPayPaymentUrlApi

urlpatterns = [
    path('payment_url/', VnPayPaymentUrlApi.as_view(), name='payment-url'),
    path('payment_ipn/', VnPayPaymentIpnApi.as_view(), name='payment-ipn'),
    path('payment_return/', VnPayPaymentReturnApi.as_view(), name='payment-return'),
]
