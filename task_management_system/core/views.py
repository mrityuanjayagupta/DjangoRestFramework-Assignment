from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_roles.granting import is_self, allof, anyof
from django.db.models import Q

from core.constants import (
    ADMIN,
    CLIENT,
    DEVELOPER,
    PROJECT_MANAGER,
    TECH_LEAD,
)
from .models import Project, Task, User
from .serializers import CustomUserDetailsSerializer, ProjectSerializer, TaskSerializer
from rest_framework.response import Response


class UserViewSet(ModelViewSet):
    serializer_class = CustomUserDetailsSerializer
    queryset = User.objects.all()
    view_permissions = {
        "create": {ADMIN: True},
        "list": {ADMIN: True},
        "retrieve": {ADMIN: True},
        "update,partial_update": {ADMIN: True},
        "options": {ADMIN: True},
        "destroy": {ADMIN: True},
    }


def is_project_member(request, view):
    user = request.user
    project = view.get_object()
    return project.members.filter(pk=user.pk).exists()


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    view_permissions = {
        "create": {
            ADMIN: True,
            PROJECT_MANAGER: True,
        },
        "list": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "retrieve": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: is_project_member,
            DEVELOPER: is_project_member,
            CLIENT: is_project_member,
        },
        "update,partial_update": {ADMIN: True, PROJECT_MANAGER: True},
        "options": {ADMIN: True, PROJECT_MANAGER: True},
        "destroy": {ADMIN: True, PROJECT_MANAGER: True},
    }

    def list(self, request):
        projects = Project.objects.all()
        user = request.user
        if user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
            projects = Project.objects.filter(members=user)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


def is_project_member_using_task(request, view):
    user = request.user
    data = request.data
    if (
        user.role == PROJECT_MANAGER
        and user.projects.filter(pk=data["project_id"]).exists()
    ):
        return True
    return user.project_members.filter(pk=data["project_id"]).exists()


def is_task_creator(request, view):
    user = request.user
    task = view.get_object()
    return task.created_by == user


def is_task_assignee(request, view):
    user = request.user
    task = view.get_object()
    return task.assigned_to == user


def is_project_member_or_creator(request, view):
    user = request.user
    task = view.get_object()
    project_id = task.project_id.id
    return (
        user.projects.filter(pk=project_id).exists()
        or user.project_members.filter(pk=project_id).exists()
    )


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    view_permissions = {
        "create": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_using_task,
            TECH_LEAD: is_project_member_using_task,
        },
        "list": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "retrieve": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_or_creator,
            TECH_LEAD: anyof(is_task_creator, is_task_assignee),
            DEVELOPER: is_task_assignee,
            CLIENT: is_task_assignee,
        },
        "update,partial_update": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_using_task,
            TECH_LEAD: anyof(is_task_creator, is_task_assignee),
        },
        "options": {ADMIN: True, PROJECT_MANAGER: True},
        "destroy": {ADMIN: True, PROJECT_MANAGER: is_project_member_or_creator},
    }

    def list(self, request):
        tasks = Task.objects.all()
        user = request.user

        if user.role == PROJECT_MANAGER:
            projects = user.project_members.all()
            tasks = Task.objects.filter(project_id__in=projects)
        elif user.role == TECH_LEAD:
            tasks = Task.objects.filter(Q(assigned_to=user) | Q(created_by=user))
        elif user.role in [DEVELOPER, CLIENT]:
            tasks = Task.objects.filter(assigned_to=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
