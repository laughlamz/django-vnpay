Django-vnpay
=====
A quick package for integrating Vnpay payment gateway.
`Version 0.0.17`

Quick start
-----------

1. Add "vnpay" to INSTALLED_APPS in `setting.py`
```
INSTALLED_APPS = [
    ...
    'vnpay',
]
```
2. Add env variable in `settings.py`
```
VNPAY_TMN_CODE = env('VNPAY_TMN_CODE')
VNPAY_HASH_SECRET_KEY = env('VNPAY_HASH_SECRET_KEY')
VNPAY_PAYMENT_URL = env('VNPAY_PAYMENT_URL')
VNPAY_RETURN_URL = env('VNPAY_RETURN_URL')
```

3. Include the vnpay URLconf in your project urls.py

```
path('vnpay/', include('vnpay.api_urls')),
```

4. Run ``python manage.py migrate`` to create related models

5. Start the development server and visit http://127.0.0.1:8000/
```
http://127.0.0.1:8000/admin/ to see the Billing
http://127.0.0.1:8000/vnpay/ to see the urls
```

Usage
-----------
1. Call api `payment_url`
- It will create billing
- It will return url to pay
2. User pay with payment_url
3. Vnpay will return result to
- api `payment_ipn`
- api `payment_return`

Note: Give the api `payment_ipn` and `payment_return` to VNPAY support.
