import json
import logging

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from vnpay.models import Billing
from vnpay.utils import VnPay

logger = logging.getLogger(__name__)


def logger_json(order_id, data):
    header = f'VNPAY_IPN {order_id}' if order_id else 'VNPAY_IPN'
    logger.info(f'{header} {json.dumps(data)}')


class VnPayPaymentIpnResponseSerializer(serializers.Serializer):
    RspCode = serializers.CharField()
    Message = serializers.CharField()


class VnPayPaymentIpnApi(APIView):

    def get_response_data(self, input_data):
        vnp = VnPay()
        response_data = vnp.validate_response_data(input_data)

        order_id = response_data['vnp_TxnRef']
        amount = int(response_data['vnp_Amount']) / 100
        vnp_response_code = response_data['vnp_ResponseCode']
        transaction_id = response_data['vnp_TransactionNo']

        if vnp.validate_hash(response_data):
            try:
                billing = Billing.objects.get(reference_number=order_id)
                if billing.amount != amount:
                    response_data = {'RspCode': '04', 'Message': 'Invalid Amount'}
                    return order_id, response_data
                if billing.status == 'NEW':
                    # TODO refactor and make reuse
                    succeeded = vnp_response_code == '00'
                    billing.finalize(succeeded=succeeded)
                    billing.status = 'CONFIRMED'
                    billing.result_payment = 'VNPAY_' + vnp_response_code
                    billing.transaction_id = transaction_id
                    billing.save(update_fields=['status', 'result_payment', 'transaction_id'])

                    # Return VNPAY: Merchant update success
                    response_data = {'RspCode': '00', 'Message': 'Confirm Success'}
                    return order_id, response_data
                else:
                    # Already Update
                    response_data = {'RspCode': '02', 'Message': 'Order Already Update'}
                    return order_id, response_data
            except Billing.DoesNotExist:
                response_data = {'RspCode': '01', 'Message': 'Order not found'}
                return order_id, response_data

        # Invalid Signature
        response_data = {'RspCode': '97', 'Message': 'Invalid Signature'}
        return order_id, response_data

    def get(self, request, *args, **kwargs):
        order_id = None

        try:
            input_data = request.GET
            if input_data:
                order_id, response_data = self.get_response_data(input_data)
            else:
                response_data = {'RspCode': '99', 'Message': 'Invalid request'}
        except Exception:  # pragma: no cover
            response_data = {'RspCode': '99', 'Message': 'Unknown error'}

        serializers = VnPayPaymentIpnResponseSerializer(data=response_data)
        serializers.is_valid(raise_exception=True)

        logger_json(order_id, response_data)
        return Response(serializers.data)
