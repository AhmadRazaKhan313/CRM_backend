from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_super_admin", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User hamesha kisi organization (tenant) ke andar hota hai.
    Role custom hota hai — UserRole table se assign hoti hai.
    Sirf is_super_admin ek special system-level flag hai.
    """
    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=120)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )

    # Sirf yeh ek system-level role hai — website owner.
    is_super_admin = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone  = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def role_names(self):
        """Sab custom roles ke naam jo is user ko assign hain."""
        return list(self.assigned_roles.values_list("role__name", flat=True))

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.employee_id:
            self.employee_id = f"EMP-{str(self.pk).zfill(4)}"
            super().save(update_fields=["employee_id"])
