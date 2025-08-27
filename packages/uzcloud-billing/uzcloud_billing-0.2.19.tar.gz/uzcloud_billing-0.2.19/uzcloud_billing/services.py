from uzcloud_billing.utils import uzcloud_service
from uzcloud_billing.models import BillingAccount
from uzcloud_billing.signals import payment_completed_signal


def create_billing_account(*, user, personType=1):
    return BillingAccount.objects.create(
        user=user,
        account_number=uzcloud_service.add_account(personType=personType),
        account_type=personType,
    )


def update_account_balance(*, account_number: str, balance: float):
    billing_account = BillingAccount.objects.get(account_number=account_number)
    billing_account.balance = balance
    billing_account.save()


def make_invoice(account_number: str, amount: float, reason: str, data: dict):
    """
    Eaxample Response :
    {
        "AccountNumber": "AA-000001",
        "ChargeAmount": 3500,
        "Balance": 109429656.176318228,
        "InvoiceId": "c3b9f00e-9c7d-4b36-a8cd-ee561041be93",
        "CreatedAt": "2022-05-07T07:07:00.8624403+00:00"
    }
    """
    response: dict = uzcloud_service.make_invoice(
        account_number=account_number, amount=amount, reason=reason
    )
    data.update(response)
    payment_completed_signal.send(sender=None, data=data)
    return response
