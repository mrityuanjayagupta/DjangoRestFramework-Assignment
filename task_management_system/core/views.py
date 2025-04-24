from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_roles.granting import is_self
from .models import Project, User
from .serializers import CustomUserDetailsSerializer, ProjectSerializer


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


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
