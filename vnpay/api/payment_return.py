import logging

from django.shortcuts import render
from rest_framework.views import APIView

from vnpay.utils import VnPay

logger = logging.getLogger(__name__)


class VnPayPaymentReturnApi(APIView):

    def get(self, request, *args, **kwargs):
        input_data = request.GET
        if not input_data:
            return render(request, 'vnpay/payment_return.html', {'title': 'Kết quả thanh toán', 'result': ''})

        vnp = VnPay()
        response_data = vnp.validate_response_data(input_data)

        order_id = response_data['vnp_TxnRef']
        amount = int(response_data['vnp_Amount']) / 100
        order_desc = response_data['vnp_OrderInfo']
        vnp_transaction_no = response_data['vnp_TransactionNo']
        vnp_response_code = response_data['vnp_ResponseCode']

        context = {
            'title': 'Kết quả thanh toán',
            'result': 'Thành công',
            'order_id': order_id,
            'amount': amount,
            'order_desc': order_desc,
            'vnp_TransactionNo': vnp_transaction_no,
            'vnp_ResponseCode': vnp_response_code,
        }

        if vnp.validate_hash(response_data):
            if not vnp_response_code == '00':
                context['result'] = 'Không thành công'
        else:
            context['result'] = 'Không thành công'
            context['msg'] = 'Sai checksum'

        return render(request, 'vnpay/payment_return.html', context)
