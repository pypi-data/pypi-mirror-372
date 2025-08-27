from typing import Union, Optional, List, Dict

from uzcloud_billing.utils import uzcloud_service
from uzcloud_billing.signals import payment_completed_signal
from uzcloud_billing.choices import TransactionTypeChoice


class BillingControllerMixin:
    def update_balance(self, balance: float):
        self.balance = balance
        self.save()

    def sync_balance(self):
        self.balance = uzcloud_service.get_balance(account_number=self.account_number)
        self.save()

    def make_charge(self, amount: float, reason: str, data: dict = {}):
        # sourcery skip: default-mutable-arg
        """
        Example Response :
        {
            "AccountNumber": "AA-000001",
            "ChargeAmount": 3500,
            "Balance": 109429656.176318228,
            "InvoiceId": "c3b9f00e-9c7d-4b36-a8cd-ee561041be93",
            "CreatedAt": "2022-05-07T07:07:00.8624403+00:00"
        }
        """
        response: dict = uzcloud_service.make_invoice(
            account_number=self.account_number, amount=amount, reason=reason
        )
        self.update_balance(balance=response["Balance"])
        data.update(response)
        payment_completed_signal.send(sender=None, data=data)
        return response

    def refund_charge(self, amount: float, invoice_id: str, reason: str):
        return uzcloud_service.refund_invoice(
            account_number=self.account_number,
            invoice_id=invoice_id,
            amount=amount,
            reason=reason,
        )

    def get_payment_links(self, amount: Union[int, float]) -> Dict:
        return uzcloud_service.generate_payment_links(
            account_number=self.account_number, amount=amount
        )

    def get_payment_providers(self) -> List:
        return uzcloud_service.payment_providers()

    def get_transaction_history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        transaction_type: Optional[TransactionTypeChoice] = None,
    ) -> List[dict]:
        return uzcloud_service.transaction_history(
            account_number=self.account_number,
            start=start,
            end=end,
            transaction_type=transaction_type,
        )
