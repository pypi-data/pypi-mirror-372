from rest_framework.permissions import BasePermission


class IsBillingGroupPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Uzcloud_Billing").exists()
