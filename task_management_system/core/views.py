from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from task_management_system.core.models import User
from task_management_system.core.serializers import CustomUserDetailsSerializer

class UserViewSet(ModelViewSet):
    serializer_class = CustomUserDetailsSerializer
    queryset = User.objects.all()