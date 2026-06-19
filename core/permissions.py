from rest_framework.permissions import BasePermission


def same_tenant(user, obj):
    if user.is_super_admin:
        return True
    return getattr(obj, "tenant_id", None) == user.tenant_id


def tenant_has_feature(user, feature_name: str) -> bool:
    if user.is_super_admin:
        return True
    try:
        return bool(getattr(user.tenant.features, feature_name, False))
    except Exception:
        return False


def user_permission_codenames(user) -> set:
    """
    User ke saare permission codenames ek set mein.
    Super admin ke paas sab kuch hota hai.
    Dashboard aur sidebar isi se decide hote hain.
    """
    if user.is_super_admin:
        from core.models import Permission
        return set(Permission.objects.values_list("codename", flat=True))

    from core.models import UserRole
    return set(
        UserRole.objects
        .filter(user=user)
        .values_list("role__permissions__codename", flat=True)
    )


def user_has_permission(user, codename: str) -> bool:
    """
    Check karta hai ke user ke kisi bhi assigned role mein yeh permission hai.
    Super admin ke paas hamesha sab permissions hoti hain.
    """
    if user.is_super_admin:
        return True
    from core.models import UserRole
    return UserRole.objects.filter(
        user=user,
        role__permissions__codename=codename,
    ).exists()


def FeatureRequired(feature_name: str):
    """Organization ke feature flag ke hisaab se access."""
    class _FeaturePermission(BasePermission):
        message = f"Your plan does not include the '{feature_name}' module."

        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            return tenant_has_feature(request.user, feature_name)

    _FeaturePermission.__name__ = f"Feature_{feature_name}"
    return _FeaturePermission


def HasPermission(codename: str):
    """
    DRF permission class — user ke custom roles mein yeh permission honi chahiye.

    Usage:
        permission_classes = (IsAuthenticated, HasPermission("leads.export"))
    """
    class _HasPermission(BasePermission):
        message = f"You don't have permission: {codename}"

        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            return user_has_permission(request.user, codename)

    _HasPermission.__name__ = f"Perm_{codename}"
    return _HasPermission


class IsSuperAdmin(BasePermission):
    """Sirf website owner (super admin)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsAuthenticatedInTenant(BasePermission):
    """
    Koi bhi logged-in user jo kisi organization ka hissa hai.
    Super admin bhi allowed.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_super_admin or request.user.tenant_id is not None


class TenantObjectPermission(BasePermission):
    """Object usi organization ka hona chahiye jisme user hai."""
    def has_object_permission(self, request, view, obj):
        return same_tenant(request.user, obj)
