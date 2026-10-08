from rest_framework.permissions import BasePermission

from api.models import Company


class IsAdminUser(BasePermission):
    """
    Grants access only to companies whose role is ADMIN.
    Deliberately checks the Company.role field, not Django's
    is_staff/is_superuser, since admin-ness here is a business
    concept on the Company model, not a Django auth concept.
    """

    def has_permission(self, request, view):
        company = getattr(request.user, 'company', None)
        if company is None:
            return False
        return company.role == Company.Role.ADMIN
