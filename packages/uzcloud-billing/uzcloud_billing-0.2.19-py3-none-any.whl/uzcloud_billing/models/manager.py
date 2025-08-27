from django.db import models

from uzcloud_billing.utils import uzcloud_service


class BillingAccountManager(models.Manager):
    def create_individual_account(self, user=None):
        return self.create(
            user=user,
            account_number=uzcloud_service.add_account(
                personType=self.model.AccountTypes.INDIVIDUAL.value
            )["accountNumber"],
            account_type=self.model.AccountTypes.INDIVIDUAL,
        )

    def create_organization_account(self, user=None):
        return self.create(
            user=user,
            account_number=uzcloud_service.add_account(
                personType=self.model.AccountTypes.ORGANIZATION.value
            )["accountNumber"],
            account_type=self.model.AccountTypes.ORGANIZATION,
        )
