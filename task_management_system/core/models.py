from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from core.constants import ADMIN, PriorityChoices, TaskStatusChoices, UserRoleChoices


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
        return self._create_user(username, email, password, role=ADMIN, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRoleChoices.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="projects"
    )
    members = models.ManyToManyField(User, related_name="project_members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_tasks"
    )
    status = models.CharField(max_length=20, choices=TaskStatusChoices.choices)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices)
    project_id = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    content = models.CharField(max_length=200)
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_comments"
    )
    task_id = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    project_id = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
