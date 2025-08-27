from django.db.models import IntegerChoices


class TransactionTypeChoice(IntegerChoices):
    ALL = 0, "all"
    PAYMENT = 1, "payment"
    INVOICE = 2, "invoice"
    REFUND = 3, "refund"
