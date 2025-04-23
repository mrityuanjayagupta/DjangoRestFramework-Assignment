from .models import User
from rest_framework import serializers


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role", "date_joined")
        read_only_fields = ["id", "date_joined"]
