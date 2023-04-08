=====
Django-vnpay
=====

This is a package that help to make payment for vnpay.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "VnPay" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'vnpay',
    ]

2. Include the VnPay URLconf in your project urls.py like this::

    path('vnpay/', include('vnpay.api_urls')),

3. Run ``python manage.py migrate`` to create the VnPay models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to see the billing (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/vnpay/ to participate in the vnpay.
