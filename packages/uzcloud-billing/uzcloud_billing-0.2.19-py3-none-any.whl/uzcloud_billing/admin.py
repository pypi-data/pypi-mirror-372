from django.contrib import admin

from .models import BillingAccount


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    list_display = [
        "account_number",
        "user",
        "account_type",
        "balance",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["user", "account_number", "account_type", "balance"]
    list_filter = ["account_type"]
    search_fields = ["account_number", "user__pk"]
    actions = ["sync_balance"]

    def has_delete_permission(self, request, obj=None):
        return False

    def sync_balance(self, request, queryset):
        for account in queryset:
            account.sync_balance()
        self.message_user(request, "Balance synced for selected accounts.")
