import pytz

from datetime import datetime
from django.contrib import admin

from vnpay.models import Billing


def get_vn_datetime(input_datetime):
    if not input_datetime:
        return '-'
    vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    utc_offset = datetime.now(vn_timezone).utcoffset()
    return (input_datetime + utc_offset).strftime('%B %d, %Y, %I:%M %p')


class BillingAdmin(admin.ModelAdmin):
    list_display = ('id', 'pay_by', 'reference_number', 'amount', 'status', 'pay_at_vn', 'created_at_vn')
    search_fields = ('id', 'pay_by__username')
    readonly_fields = ('pay_at_vn', 'created_at_vn')

    def pay_at_vn(self, obj):
        return get_vn_datetime(obj.pay_at)

    def created_at_vn(self, obj):
        return get_vn_datetime(obj.created_at)


# Register your models here.
admin.site.register(Billing, BillingAdmin)
