====================
Uzcloud Billing
====================

Uzcloud Billing is a Django app to provide account with Uzcloud Billing account number. 


Quick start
-----------

1.Add "rest_framework" and "uzcloud_billing" to your INSTALLED_APPS :

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'uzcloud_billing',
    ]

2.Include the uzcloud_billing urls in your project urls.py like this :

.. code-block:: python

    path('api/billing/', include('uzcloud_billing.urls')),

3.Add Following credentials to settings.py :

.. code-block:: python

    UZCLOUD_BILLING = {
        "AUTH_URL": "",
        "BASE_URL": "",
        "CLIENT_ID": "",
        "CLIENT_SECRET": "",
        "IDENT_RESPONSE_SERIALIZER": "",
    }
    

4.Run ``python manage.py migrate`` to create the uzcloud_billing models.
5.You may create receiver for balance filled event.Signal for your receiver must be ``uzcloud_billing.signals.balance_filled_signal``.
Receiver function get  ``data`` as argument and data value is {"AccountNumber":"","paymentType":"","Amount":"","Balance":""}
