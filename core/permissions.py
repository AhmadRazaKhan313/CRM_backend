from rest_framework.permissions import BasePermission

ROLE_HIERARCHY = {
    "super_admin": 100,
    "ceo": 90,
    "coo": 80,
    "dept_head": 70,
    "sales_director": 65,
    "lead_manager": 50,
    "sales_manager": 50,
    "lead_employee": 30,
    "sales_employee": 30,
}


def has_role(user, *roles):
    if user.is_super_admin:
        return True
    return user.role in roles


def same_tenant(user, obj):
    if user.is_super_admin:
        return True
    return getattr(obj, "tenant_id", None) == user.tenant_id


def same_department(user, obj):
    if user.role in ("ceo", "coo"):
        return True
    return getattr(obj, "department", None) == user.department


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsCEOOrAbove(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_role(request.user, "ceo")


class IsCOOOrAbove(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_role(request.user, "ceo", "coo")


class IsDeptHeadOrAbove(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_role(request.user, "ceo", "coo", "dept_head")


class IsSalesDirectorOrAbove(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_role(request.user, "ceo", "coo", "dept_head", "sales_director")


class IsManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_role(
            request.user,
            "ceo", "coo", "dept_head", "sales_director",
            "lead_manager", "sales_manager"
        )


class IsAnyEmployee(BasePermission):
    """Any authenticated user of the tenant."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.tenant_id is not None or request.user.is_super_admin
        )


class TenantObjectPermission(BasePermission):
    """Object-level — user can only access objects in their tenant."""
    def has_object_permission(self, request, view, obj):
        return same_tenant(request.user, obj)


class DepartmentObjectPermission(BasePermission):
    """Object-level — user can only access objects in their department."""
    def has_object_permission(self, request, view, obj):
        if not same_tenant(request.user, obj):
            return False
        return same_department(request.user, obj)