from django.conf import settings
from django.db import models
from django.utils import timezone
from ipware import get_client_ip

from vnpay.utils import VnPay

STATUS_CHOICES = (
    ('NEW', 'NEW'),
    ('CONFIRMED', 'CONFIRMED'),
)

RESULT_CHOICES = (
    ('VNPAY_00', 'VNPAY SUCCESS'),
    ('VNPAY_05', 'VNPAY BAD_PASSWORD_EXCEEDING'),
    ('VNPAY_06', 'VNPAY WRONG_PASSWORD'),
    ('VNPAY_07', 'VNPAY SUSPICIOUS_TRANSACTION'),
    ('VNPAY_12', 'VNPAY CARD_IS_LOCKED'),
    ('VNPAY_09', 'VNPAY NO_INTERNET_BANKING'),
    ('VNPAY_10', 'VNPAY VERIFICATION_EXCEEDING'),
    ('VNPAY_11', 'VNPAY TIMEOUT_PAYMENT'),
    ('VNPAY_24', 'VNPAY CUSTOMER_CANCEL'),
    ('VNPAY_51', 'VNPAY NOT_ENOUGH_BALANCE'),
    ('VNPAY_65', 'VNPAY TRANSACTION_PER_DAY_EXCEEDING'),
    ('VNPAY_75', 'VNPAY BANK_MAINTENANCE'),
    ('VNPAY_99', 'VNPAY OTHER_ERRORS'),
)


class Billing(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(default='VND', max_length=3)
    pay_at = models.DateTimeField(null=True, blank=True)
    pay_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    reference_number = models.CharField(
        max_length=100, help_text='Reference number from payment gateway', blank=True,
        null=True,
    )

    status = models.CharField(choices=STATUS_CHOICES, default='NEW', max_length=20)
    result_payment = models.CharField(choices=RESULT_CHOICES, max_length=50, null=True)
    is_paid = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    def set_paid(self):
        self.result_payment = 'succeeded'
        self.result_payment = 'VNPAY_00'
        self.pay_at = timezone.now()
        self.is_paid = True

    def finalize(self, succeeded):
        if not succeeded:
            return
        self.set_paid()
        self.save()

    def get_payment_url(self, request):
        ipaddr, is_routable = get_client_ip(request)

        vnp = VnPay()
        request_data = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': settings.VNPAY_TMN_CODE,
            'vnp_Amount': int(self.amount * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': self.reference_number,
            'vnp_OrderInfo': f'Thanh toán hóa đơn {self.reference_number}',
            'vnp_OrderType': 'billpayment',
            'vnp_Locale': 'vn',
            'vnp_CreateDate': timezone.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': ipaddr,
            'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
        }
        return vnp.get_payment_url(request_data)
