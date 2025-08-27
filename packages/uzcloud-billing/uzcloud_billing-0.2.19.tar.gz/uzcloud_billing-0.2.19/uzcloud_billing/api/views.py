from django.conf import settings
from django.utils.module_loading import import_string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from uzcloud_billing.models import BillingAccount
from uzcloud_billing.services import update_account_balance
from uzcloud_billing.signals import balance_filled_signal
from .serializers import PaymentEventSerializer, IdentSerializer
from .permissions import IsBillingGroupPermission


class BalanceFilledEventView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, IsBillingGroupPermission]

    def post(self, request, *args, **kwargs):
        serializer = PaymentEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_account_balance(
            account_number=serializer.validated_data["AccountNumber"],
            balance=serializer.validated_data["Balance"],
        )
        serializer.billing_account.refresh_from_db()
        balance_filled_signal.send(
            sender=BillingAccount,
            instance=serializer.billing_account,
            data=serializer.validated_data,
        )
        return Response()


class IdentEventView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, IsBillingGroupPermission]

    def post(self, request, *args, **kwargs):
        serializer = IdentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_serializer = import_string(
            settings.UZCLOUD_BILLING["IDENT_RESPONSE_SERIALIZER"]
        )
        return Response(
            response_serializer(instance=serializer.billing_account.user).data
        )
