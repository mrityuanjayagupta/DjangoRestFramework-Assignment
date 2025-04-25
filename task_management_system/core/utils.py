from core.constants import PROJECT_MANAGER, TECH_LEAD
from .models import Project, Task
from django.db.models import Q
from rest_framework_roles.granting import is_self
from rest_framework import serializers


def is_user_in_projects(request, view):
    user = request.user
    target_user = view.get_object()
    projects = Project.objects.filter(Q(created_by=user) | Q(members=user)).distinct()
    return Project.objects.filter(
        Q(members=target_user) | Q(created_by=target_user), id__in=projects
    ).exists()


def is_allowed_to_retrieve(request, view):
    return is_self(request, view) or is_user_in_projects(request, view)


def is_project_member(request, view):
    user = request.user
    project = view.get_object()
    return project.members.filter(pk=user.pk).exists()


def is_project_creator(request, view):
    user = request.user
    project = view.get_object()
    return project.created_by == user


def is_project_member_using_task(request, view):
    user = request.user
    data = request.data
    project_id = data.get("project_id")
    if project_id is None:
        raise serializers.ValidationError({"project": "Missing Project Field"})
    if user.role == PROJECT_MANAGER and user.projects.filter(pk=project_id).exists():
        return True
    return user.project_members.filter(pk=project_id).exists()


def is_task_creator(request, view):
    user = request.user
    task = view.get_object()
    return task.created_by == user


def is_task_assignee(request, view):
    user = request.user
    task = view.get_object()
    return task.assigned_to == user


def is_project_member_or_creator_using_task(request, view):
    user = request.user
    task = view.get_object()
    project_id = task.project_id.id
    return (
        user.projects.filter(pk=project_id).exists()
        or user.project_members.filter(pk=project_id).exists()
    )


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


def is_comment_author(request, view):
    user = request.user
    comment = view.get_object()
    return comment.author == user
