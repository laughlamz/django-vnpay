from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from vnpay.models import Billing
from vnpay.utils import hmacsha512


class BaseUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test',
        )
        self.client.force_authenticate(self.user)


class BaseBilling(BaseUserTest):
    def setUp(self):
        super().setUp()
        self.billing = Billing.objects.create(
            pay_by=self.user,
            status='NEW',
            amount=100000,
            reference_number='00001111',
        )

    def _get_query_string(self, vnp_Amount=10000000, vnp_ResponseCode='00', vnp_TxnRef='00001111'):  # default success
        return f'vnp_Amount={vnp_Amount}' \
               '&vnp_BankCode=NCB' \
               '&vnp_BankTranNo=VNP12345678' \
               '&vnp_CardType=ATM' \
               f'&vnp_OrderInfo=Thanh+toan+vnpay+hoa+don+{vnp_TxnRef}' \
               '&vnp_PayDate=20230328175935' \
               f'&vnp_ResponseCode={vnp_ResponseCode}' \
               '&vnp_TmnCode=EOH00000' \
               '&vnp_TransactionNo=12345678' \
               '&vnp_TransactionStatus=00' \
               f'&vnp_TxnRef={vnp_TxnRef}'

    def _call_api(self, query_string, has_secure_type=False):
        hash_result = hmacsha512(settings.VNPAY_HASH_SECRET_KEY, query_string)
        url = f'{self.url}?{query_string}&vnp_SecureHash={hash_result}'

        if has_secure_type:
            url += '&vnp_SecureHashType=SHA256'

        return self.client.get(url)


class VnPayPaymentUrlApiTest(BaseUserTest):
    def test_payment_url(self):
        url = reverse('payment-url')
        data = {
            'amount': 1000000,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('payment_url', response.data)
        self.assertTrue(response.data['payment_url'])

        self.assertTrue(Billing.objects.filter(pay_by=self.user).exists())
        billing = Billing.objects.get(pay_by=self.user)

        self.assertEqual(billing.amount, data['amount'])
        self.assertEqual(billing.currency, 'VND')
        self.assertEqual(billing.status, 'NEW')

        self.assertTrue(billing.reference_number)
        self.assertTrue(billing.created_at)
        self.assertTrue(billing.updated_at)
        self.assertTrue(billing.id)


class VnPayPaymentIpnApiTests(BaseBilling):
    url = reverse('payment-ipn')

    def _assert_response_success(self, response, assert_response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, assert_response)

    def test_vnpay_payment_ipn_view_get(self):
        response = self.client.get(self.url)
        self._assert_response_success(response, {'RspCode': '99', 'Message': 'Invalid request'})

    def test_vnpay_payment_ipn_wrong_secret_key(self):
        query_string = self._get_query_string()
        response = self.client.get(f'{self.url}?{query_string}&vnp_SecureHash=wrong_hash_key&vnp_SecureHashType=SHA256')
        self._assert_response_success(response, {'RspCode': '97', 'Message': 'Invalid Signature'})

    def test_vnpay_payment_ipn_right_secret_key_billing_updated(self):
        self.billing.status = 'CONFIRMED'
        self.billing.save()

        query_string = self._get_query_string()
        response = self._call_api(query_string)
        self._assert_response_success(
            response, {'RspCode': '02', 'Message': 'Order Already Update'},
        )

    def test_vnpay_payment_ipn_success(self):
        query_string = self._get_query_string()
        response = self._call_api(query_string)
        self._assert_response_success(response, {'RspCode': '00', 'Message': 'Confirm Success'})

        self.billing.refresh_from_db()
        self.assertEqual(self.billing.result_payment, 'VNPAY_00')

    def test_vnpay_payment_ipn_success_but_payment_not_success(self):
        query_string = self._get_query_string(vnp_ResponseCode='99')
        response = self._call_api(query_string)
        self._assert_response_success(response, {'RspCode': '00', 'Message': 'Confirm Success'})

        self.billing.refresh_from_db()
        self.assertEqual(self.billing.result_payment, 'VNPAY_99')

    def test_vnpay_payment_ipn_order_not_found(self):
        query_string = self._get_query_string(vnp_TxnRef='999999999')
        response = self._call_api(query_string)
        self._assert_response_success(response, {'RspCode': '01', 'Message': 'Order not found'})

    def test_vnpay_payment_ipn_invalid_amount(self):
        query_string = self._get_query_string(vnp_Amount=1000)
        response = self._call_api(query_string)
        self._assert_response_success(response, {'RspCode': '04', 'Message': 'Invalid Amount'})


class VnPayPaymentReturnApiTests(BaseBilling):
    url = reverse('payment-return')

    def test_vnpay_payment_return_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_vnpay_payment_return_right_secret_key_payment_success(self):
        query_string = self._get_query_string()
        response = self._call_api(query_string)
        self.assertEqual(response.status_code, 200)
        self.assertIn('- Thành công'.encode(), response.content)

    def test_vnpay_payment_has_secure_type(self):
        query_string = self._get_query_string()
        response = self._call_api(query_string, True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('- Thành công'.encode(), response.content)

    def test_vnpay_payment_return_right_secrect_key_payment_failed(self):
        query_string = self._get_query_string(vnp_ResponseCode='99')
        response = self._call_api(query_string)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Không thành công'.encode(), response.content)

    def test_vnpay_payment_return_wrong_checksum(self):
        query_string = self._get_query_string(vnp_ResponseCode='00')
        url = f'{self.url}?{query_string}&vnp_SecureHash=123'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Không thành công'.encode(), response.content)
        self.assertIn('Sai checksum'.encode(), response.content)
