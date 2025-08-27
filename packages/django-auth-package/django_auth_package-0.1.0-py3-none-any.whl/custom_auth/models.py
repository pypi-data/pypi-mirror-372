from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def get_default_role():
    """
    Returns the default role from settings.AUTH_DEFAULT_ROLE
    """
    return getattr(settings, "AUTH_DEFAULT_ROLE", None)


def validate_role(value):
    """
    Validates role against AUTH_ROLES in settings.
    """
    roles = getattr(settings, "AUTH_ROLES", [])
    if roles and value not in roles:
        raise ValidationError(f"Role '{value}' is not valid. Allowed roles: {roles}")

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        if "role" not in extra_fields:
            extra_fields["role"] = get_default_role()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        roles = getattr(settings, "AUTH_ROLES", [])
        if "role" not in extra_fields and "admin" in roles:
            extra_fields["role"] = "admin"

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(
        max_length=50,
        default=get_default_role,
        validators=[validate_role],
        blank=True,  # allow blank when AUTH_MODE="simple"
        null=True,
    )
    is_active = models.BooleanField(default=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Returns the full name of the user.
        """
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email