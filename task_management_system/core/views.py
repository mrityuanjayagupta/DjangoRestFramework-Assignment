from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import User
from .serializers import CustomUserDetailsSerializer


class UserViewSet(ModelViewSet):
    serializer_class = CustomUserDetailsSerializer
    queryset = User.objects.all()
