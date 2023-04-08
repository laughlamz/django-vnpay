Django-vnpay
=====
A quick package for integrating Vnpay payment gateway.
`Version 0.0.7`

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

5. Start the development server and visit http://0.0.7.1:8000/
```
http://0.0.7.1:8000/admin/ to see the Billing
http://0.0.7.1:8000/vnpay/ to see the urls
```
