from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from uzcloud_billing.models import BillingAccount

User = get_user_model()


class Command(BaseCommand):
    help = "Create Billing Account for Users who don't have billing account"

    def handle(self, *args, **options):
        users_has_no_billing_accounts = User.objects.filter(
            billing_account__isnull=True
        )
        if users_has_no_billing_accounts.exists():
            for user in users_has_no_billing_accounts:
                BillingAccount.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully {users_has_no_billing_accounts.count()} BillingAccounts have been created!"
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE("All users have already owned billing accounts")
            )
