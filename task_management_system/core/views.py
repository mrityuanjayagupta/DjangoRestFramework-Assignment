from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_roles.granting import is_self, anyof
from rest_framework import serializers
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.core.paginator import Paginator

from core.constants import (
    ADMIN,
    CLIENT,
    DEVELOPER,
    PAGE_SIZE,
    PROJECT_MANAGER,
    TECH_LEAD,
)
from core.utils import (
    check_comment,
    is_allowed_to_retrieve,
    is_comment_author,
    is_project_creator,
    is_project_member,
    is_project_member_or_creator_using_task,
    is_project_member_using_comment,
    is_project_member_using_task,
    is_task_assignee,
    is_task_creator,
)
from .models import Project, Task, User, Comment
from .serializers import (
    CommentSerializer,
    CustomUserDetailsSerializer,
    ProjectSerializer,
    TaskSerializer,
)


class UserViewSet(ModelViewSet):
    """
    ViewSet for User model with role-based permissions and caching.
    Supports listing users with pagination and restricted access based on roles.
    """

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
        "update,partial_update": {ADMIN: True},
        "options": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "destroy": {ADMIN: True},
    }

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        """
        List users with role-based filtering and pagination.
        Project managers see users associated with their projects.
        Tech leads, developers, and clients see an empty list.
        """
        try:
            users = User.objects.all()
        except Exception as e:
            return Response(
                {"detail": f"Error retrieving users: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        page = request.GET.get("page", 1)
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
            users = User.objects.filter(
                Q(project_members__in=projects) | Q(projects__in=projects)
            ).distinct()
        elif user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
            users = User.objects.none()
        try:
            paginator = Paginator(users, PAGE_SIZE)
            serializer = self.get_serializer(paginator.page(page), many=True)
        except Exception as e:
            return Response(
                {"detail": "page is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class ProjectViewSet(ModelViewSet):
    """
    ViewSet for Project model with role-based permissions and caching.
    Supports listing projects with pagination and restricted access based on roles.
    """

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
            PROJECT_MANAGER: anyof(is_project_creator, is_project_member),
            TECH_LEAD: is_project_member,
            DEVELOPER: is_project_member,
            CLIENT: is_project_member,
        },
        "update,partial_update": {
            ADMIN: True,
            PROJECT_MANAGER: anyof(is_project_creator, is_project_member),
        },
        "options": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "destroy": {
            ADMIN: True,
            PROJECT_MANAGER: anyof(is_project_creator, is_project_member),
        },
    }

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        """
        List projects with filtering based on user role:
        - Project Managers see projects they created or are members of.
        - Tech Leads, Developers, and Clients see projects they are members of.
        - Admins see all projects.
        """
        try:
            projects = Project.objects.all()
        except Exception as e:
            return Response(
                {"detail": f"Error retrieving projects: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        name = request.GET.get("name", "").strip()
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(members=user) | Q(created_by=user)
            ).distinct()
        elif user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
            projects = Project.objects.filter(members=user)

        if name:
            projects = projects.filter(name__icontains=name)

        page = request.GET.get("page", 1)
        try:
            paginator = Paginator(projects, PAGE_SIZE)
            Sserializer = self.get_serializer(paginator.page(page), many=True)
        except Exception as e:
            return Response(
                {"detail": "page is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class TaskViewSet(ModelViewSet):
    """
    ViewSet for Task model with role-based permissions and caching.
    Supports listing tasks with pagination and restricted access based on roles.
    """

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
            PROJECT_MANAGER: is_project_member_or_creator_using_task,
            TECH_LEAD: anyof(is_task_creator, is_task_assignee),
            DEVELOPER: is_task_assignee,
            CLIENT: is_task_assignee,
        },
        "update,partial_update": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_using_task,
            TECH_LEAD: anyof(is_task_creator, is_task_assignee),
        },
        "options": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "destroy": {
            ADMIN: True,
            PROJECT_MANAGER: is_project_member_or_creator_using_task,
        },
    }

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        """
        List tasks with filtering based on user role:
        - Project Managers see tasks related to projects they are part of.
        - Tech Leads see assigned and created tasks.
        - Developers and Clients see only assigned tasks.
        Implements pagination and error handling.
        """
        try:
            tasks = Task.objects.all()
        except Exception as e:
            return Response(
                {"detail": f"Error retrieving tasks: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        title = request.GET.get("title", "").strip()
        if user.role == PROJECT_MANAGER:
            projects = user.project_members.all()
            tasks = Task.objects.filter(project_id__in=projects)
        elif user.role == TECH_LEAD:
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()
        elif user.role in [DEVELOPER, CLIENT]:
            tasks = Task.objects.filter(assigned_to=user)
        if title:
            tasks = tasks.filter(title__icontains=title)
        page = request.GET.get("page", 1)
        try:
            paginator = Paginator(tasks, PAGE_SIZE)
            serializer = self.get_serializer(paginator.page(page), many=True)
        except Exception as e:
            return Response(
                {"detail": "page is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    """
    ViewSet for Comment model with role-based permissions and caching.
    Supports listing comments with pagination and restricted access based on roles.
    """

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
        "update,partial_update": {
            ADMIN: True,
            PROJECT_MANAGER: is_comment_author,
            TECH_LEAD: is_comment_author,
            DEVELOPER: is_comment_author,
            CLIENT: is_comment_author,
        },
        "options": {
            ADMIN: True,
            PROJECT_MANAGER: True,
            TECH_LEAD: True,
            DEVELOPER: True,
            CLIENT: True,
        },
        "destroy": {
            ADMIN: True,
            PROJECT_MANAGER: check_comment,
            TECH_LEAD: check_comment,
            DEVELOPER: check_comment,
        },
    }

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        """
        List comments with filtering based on user role:
        - Shows comments for tasks or projects where the user is a member.
        - Admin sees all comments.
        Implements pagination and error handling.
        """
        try:
            comments = Comment.objects.all()
            projects = Project.objects.all()
        except Exception as e:
            return Response(
                {"detail": f"Error retrieving comments/projects: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        page = request.GET.get("page", 1)
        if user.role == PROJECT_MANAGER:
            projects = Project.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(project_id__in=projects)
            ).distinct()
            task_ids = tasks.values_list("id", flat=True)
            project_ids = projects.values_list("id", flat=True)

            comments = Comment.objects.filter(
                Q(task_id__in=task_ids) | Q(project_id__in=project_ids)
            ).distinct()
        elif user.role in [TECH_LEAD, DEVELOPER, CLIENT]:
            tasks = Task.objects.filter(
                Q(assigned_to=user) | Q(created_by=user)
            ).distinct()
            projects = Project.objects.filter(members=user)
            task_ids = tasks.values_list("id", flat=True)
            project_ids = projects.values_list("id", flat=True)

            comments = Comment.objects.filter(
                Q(task_id__in=task_ids) | Q(project_id__in=project_ids)
            ).distinct()
        try:
            paginator = Paginator(comments, PAGE_SIZE)
            serializer = self.get_serializer(paginator.page(page), many=True)
        except Exception as e:
            return Response(
                {"detail": "page is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data)
