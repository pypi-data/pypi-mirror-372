from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from uzcloud_billing.models import BillingAccount

User = get_user_model()


class BaseAccountNumberSerializer(serializers.Serializer):
    AccountNumber = serializers.CharField(max_length=16, min_length=9)

    def validate_AccountNumber(self, value):
        account = BillingAccount.objects.filter(account_number=value)
        if not account.exists():
            raise NotFound(detail={"error_code": "account_number_not_exist"})
        self.billing_account: BillingAccount = account.first()
        return value


class PaymentEventSerializer(BaseAccountNumberSerializer):
    PaymentType = serializers.CharField(max_length=20)
    Amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    Balance = serializers.DecimalField(max_digits=10, decimal_places=2)


class IdentSerializer(BaseAccountNumberSerializer):
    pass


class IdentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_active"]
