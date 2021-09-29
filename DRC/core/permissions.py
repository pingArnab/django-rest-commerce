from rest_framework.permissions import BasePermission
from USER.models import UserProfile
from SELLER.models import Seller


class UserOnly(BasePermission):
    message = 'Account not found'

    def has_permission(self, request, view):
        return bool(UserProfile.objects.filter(user__username=request.user.username))


class SellerOnly(BasePermission):
    message = 'Seller account not found'

    def has_permission(self, request, view):
        return bool(Seller.objects.filter(user__username=request.user.username))


class VerifiedSeller(BasePermission):
    message = 'Seller not verified'

    def has_permission(self, request, view):
        return bool(request.user.seller.verified)


class IsNotAuthenticated(BasePermission):
    message = 'You are already signed in'

    def has_permission(self, request, view):
        return not request.user.is_authenticated
