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
from .models import Project, Task, User, Comment
from .serializers import (
    CommentSerializer,
    CustomUserDetailsSerializer,
    ProjectSerializer,
    TaskSerializer,
)
from rest_framework.response import Response


def is_user_in_projects(request, view):
    user = request.user
    target_user = view.get_object()
    print(user)
    print(target_user)
    projects = Project.objects.filter(Q(created_by=user) | Q(members=user)).distinct()
    return Project.objects.filter(
        Q(members=target_user) | Q(created_by=target_user), id__in=projects
    ).exists()


def is_allowed_to_retrieve(request, view):
    return is_self(request, view) or is_user_in_projects(request, view)


class UserViewSet(ModelViewSet):
    serializer_class = CustomUserDetailsSerializer
    queryset = User.objects.all()
    view_permissions = {
        "create": {ADMIN: True},
        "list": {ADMIN: True, PROJECT_MANAGER: True},
        "retrieve": {
            ADMIN: True,
            PROJECT_MANAGER: is_allowed_to_retrieve,
            TECH_LEAD: is_self,
            DEVELOPER: is_self,
            CLIENT: is_self,
        },
        "update,partial_update": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            CLIENT: is_self,
            DEVELOPER: is_self,
            CLIENT: is_self,
        },
        "options": {ADMIN: True},
        "destroy": {ADMIN: True},
    }

    def list(self, request):
        users = User.objects.all()
        user = request.user
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
            users = User.objects.filter(
                Q(project_members__in=projects) | Q(projects__in=projects)
            ).distinct()
        else:
            users = User.objects.none()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


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
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(members=user) | Q(created_by=user)
            ).distinct()
        elif user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
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
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()
        elif user.role in [DEVELOPER, CLIENT]:
            tasks = Task.objects.filter(assigned_to=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


def check_comment_using_task_and_project(user, project_id, task_id):
    if project_id:
        if (
            user.role == PROJECT_MANAGER
            and user.projects.filter(pk=project_id).exists()
        ):
            return True
        return user.project_members.filter(pk=project_id).exists()
    elif task_id:
        task = Task.objects.get(id=task_id)
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(members=user) | Q(created_by=user)
            ).distinct()
            return (task.assigned_to == user) or (task.project_id in projects)
        elif user.role == TECH_LEAD:
            return Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user), id=task_id
            ).exists()
        else:
            return task.assigned_to == user


def is_project_member_using_comment(request, view):
    user = request.user
    data = request.data
    if data.get("project_id") and data.get("task_id"):
        return False
    project_id = data.get("project_id")
    task_id = data.get("task_id")
    return check_comment_using_task_and_project(user, project_id, task_id)


def check_comment(request, view):
    user = request.user
    comment = view.get_object()
    project_id = None
    task_id = None
    if comment.project_id:
        project_id = comment.project_id.id
    if comment.task_id:
        task_id = comment.task_id.id
    return check_comment_using_task_and_project(user, project_id, task_id)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    view_permissions = {
        "create": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_using_comment,
            TECH_LEAD: is_project_member_using_comment,
            DEVELOPER: is_project_member_using_comment,
            CLIENT: is_project_member_using_comment,
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
            PROJECT_MANAGER: check_comment,
            TECH_LEAD: check_comment,
            DEVELOPER: check_comment,
            CLIENT: check_comment,
        },
        "options": {ADMIN: True, PROJECT_MANAGER: True},
        "destroy": {
            ADMIN: True,
            PROJECT_MANAGER: check_comment,
            TECH_LEAD: check_comment,
            DEVELOPER: check_comment,
        },
    }

    def list(self, request):
        tasks = Comment.objects.all()
        user = request.user

        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(project_id__in=projects)
            ).distinct()
        elif user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()
            projects = Project.objects.filter(members=user)
        comments = Comment.objects.filter(
            Q(task_id__in=tasks) | Q(project_id__in=projects)
        ).distinct()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
