class TenantQuerysetMixin:
    """
    View mixin — queryset ko automatically organization (tenant) pe filter karta hai.
    Super admin ko sab data milta hai.
    """
    def get_queryset(self):
        qs   = super().get_queryset()
        user = self.request.user
        if user.is_super_admin:
            return qs
        return qs.filter(tenant=user.tenant)
