from django.urls import path
from uzcloud_billing.api.views import BalanceFilledEventView, IdentEventView

urlpatterns = [
    path("payment/send_payment_event/", BalanceFilledEventView.as_view()),
    path("payment/ident/", IdentEventView.as_view()),
]
