from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_MANAGER = "PROJECT_MANAGER", "Project Manager"
    TECH_LEAD = "TECH_LEAD", "Tech Lead"
    DEVELOPER = "DEVELOPER", "Developer"
    CLIENT = "CLIENT", "Client"


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, role, **extra_fields):
        if not username:
            raise ValueError("User must have username")
        if not email:
            raise ValueError("User must have email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, role, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, role, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(
            username, email, password, role="ADMIN", **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
