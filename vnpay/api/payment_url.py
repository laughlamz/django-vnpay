from django.utils import timezone

from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from vnpay.models import Billing


class VnPayPaymentUrlSerializer(serializers.Serializer):
    amount = serializers.IntegerField()


class VnPayPaymentUrlApi(GenericAPIView):
    serializer_class = VnPayPaymentUrlSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        billing = Billing.objects.create(
            status='NEW',
            currency='VND',
            pay_by=self.request.user,
            amount=serializer.validated_data['amount'],
            reference_number=timezone.now().strftime('%Y%m%d%H%M%S'),
        )

        payment_url = billing.get_payment_url(request)
        return Response({'payment_url': payment_url})
