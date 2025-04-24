from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_roles.granting import is_self, allof
from .models import Project, Task, User
from .serializers import CustomUserDetailsSerializer, ProjectSerializer, TaskSerializer
from rest_framework.response import Response


class UserViewSet(ModelViewSet):
    serializer_class = CustomUserDetailsSerializer
    queryset = User.objects.all()
    view_permissions = {
        "create": {"ADMIN": True},
        "list": {"ADMIN": True},
        "retrieve": {"ADMIN": True},
        "update,partial_update": {"ADMIN": True},
        "options": {"ADMIN": True},
    }


def is_project_member(request, view):
    user = request.user
    project = view.get_object()
    return project.members.filter(pk=user.pk).exists()


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    view_permissions = {
        "create": {"ADMIN": True, "PROJECT_MANAGER": True},
        "list": {
            "ADMIN": True,
            "PROJECT_MANAGER": True,
            "TECH_LEAD": True,
            "DEVELOPER": True,
            "CLIENT": True,
        },
        "retrieve": {
            "ADMIN": True,
            "PROJECT_MANAGER": True,
            "TECH_LEAD": is_project_member,
            "DEVELOPER": is_project_member,
            "CLIENT": is_project_member,
        },
        "update,partial_update": {"ADMIN": True, "PROJECT_MANAGER": True},
        "options": {"ADMIN": True, "PROJECT_MANAGER": True},
        "destroy": {"ADMIN": True, "PROJECT_MANAGER": True},
    }

    def list(self, request):
        projects = Project.objects.all()
        user = request.user
        if (
            user.role == "TECH_LEAD"
            or user.role == "DEVELOPER"
            or user.role == "CLIENT"
        ):
            projects = Project.objects.filter(members=request.user)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
