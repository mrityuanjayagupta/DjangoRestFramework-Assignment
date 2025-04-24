from rest_framework_roles.roles import is_user, is_anon, is_admin

from task_management_system.core.constants import (
    ADMIN,
    CLIENT,
    DEVELOPER,
    PROJECT_MANAGER,
    TECH_LEAD,
    UserRoleChoices,
)


def is_project_manager(request, view):
    return is_user(request, view) and request.user.role == "PROJECT_MANAGER"


def is_tech_lead(request, view):
    return is_user(request, view) and request.user.role == "TECH_LEAD"


def is_developer(request, view):
    return is_user(request, view) and request.user.role == "DEVELOPER"


def is_client(request, view):
    return is_user(request, view) and request.user.role == "CLIENT"


ROLES = {
    ADMIN: is_admin,
    PROJECT_MANAGER: is_project_manager,
    TECH_LEAD: is_tech_lead,
    DEVELOPER: is_developer,
    CLIENT: is_client,
}
