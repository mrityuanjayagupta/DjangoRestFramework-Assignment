from rest_framework_roles.roles import is_user

from core.constants import ADMIN, CLIENT, DEVELOPER, PROJECT_MANAGER, TECH_LEAD


def is_admin(request, view):
    return is_user(request, view) and request.user.role == ADMIN


def is_project_manager(request, view):
    return is_user(request, view) and request.user.role == PROJECT_MANAGER


def is_tech_lead(request, view):
    return is_user(request, view) and request.user.role == TECH_LEAD


def is_developer(request, view):
    return is_user(request, view) and request.user.role == DEVELOPER


def is_client(request, view):
    return is_user(request, view) and request.user.role == CLIENT


ROLES = {
    ADMIN: is_admin,
    PROJECT_MANAGER: is_project_manager,
    TECH_LEAD: is_tech_lead,
    DEVELOPER: is_developer,
    CLIENT: is_client,
}
