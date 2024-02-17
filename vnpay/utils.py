import hashlib
import hmac
from urllib.parse import quote_plus

from django.conf import settings
from rest_framework import serializers


# https://sandbox.vnpayment.vn/apis/docs/thanh-toan-pay/pay.html#code-ipn-url
class VnPaySerializer(serializers.Serializer):
    vnp_TmnCode = serializers.CharField()
    vnp_Amount = serializers.CharField()
    vnp_BankCode = serializers.CharField()
    vnp_BankTranNo = serializers.CharField(required=False)
    vnp_CardType = serializers.CharField(required=False)
    vnp_PayDate = serializers.CharField(required=False)
    vnp_OrderInfo = serializers.CharField()
    vnp_TransactionNo = serializers.CharField()
    vnp_ResponseCode = serializers.CharField()
    vnp_TransactionStatus = serializers.CharField()
    vnp_TxnRef = serializers.CharField()
    vnp_SecureHashType = serializers.CharField(required=False)
    vnp_SecureHash = serializers.CharField()


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


class VnPay:
    requestData = {}

    def get_query_string_and_hash(self, data):
        input_data = sorted(data.items())
        query_string = ''
        seq = 0
        for key, val in input_data:
            if seq == 1:
                query_string += f'&{key}={quote_plus(str(val))}'
            else:
                seq = 1
                query_string = f'{key}={quote_plus(str(val))}'

        hash_value = hmacsha512(settings.VNPAY_HASH_SECRET_KEY, query_string)
        return query_string, hash_value

    def get_payment_url(self, request_data):
        query_string, hash_value = self.get_query_string_and_hash(request_data)
        return f'{settings.VNPAY_PAYMENT_URL}?{query_string}&vnp_SecureHash={hash_value}'

    def validate_response_data(self, response_data):
        serializers = VnPaySerializer(data=response_data)
        serializers.is_valid(raise_exception=True)
        return serializers.validated_data

    def validate_hash(self, response_data):
        vnp_secure_hash = response_data.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in response_data.keys():
            response_data.pop('vnp_SecureHashType')

        _, hash_value = self.get_query_string_and_hash(response_data)
        return vnp_secure_hash == hash_value
