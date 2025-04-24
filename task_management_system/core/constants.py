from django.db import models


class UserRoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_MANAGER = "PROJECT_MANAGER", "Project Manager"
    TECH_LEAD = "TECH_LEAD", "Tech Lead"
    DEVELOPER = "DEVELOPER", "Developer"
    CLIENT = "CLIENT", "Client"


ADMIN = UserRoleChoices.ADMIN.value
PROJECT_MANAGER = UserRoleChoices.PROJECT_MANAGER.value
TECH_LEAD = UserRoleChoices.TECH_LEAD.value
DEVELOPER = UserRoleChoices.DEVELOPER.value
CLIENT = UserRoleChoices.CLIENT.value


class TaskStatusChoices(models.TextChoices):
    TO_DO = "TO_DO", "To Do"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    DONE = "DONE", "Done"


class PriorityChoices(models.TextChoices):
    LOW = "LOW", "Low Priority"
    MEDIUM = "MEDIUM", "Medium Priority"
    HIGH = "HIGH", "High Priority"
