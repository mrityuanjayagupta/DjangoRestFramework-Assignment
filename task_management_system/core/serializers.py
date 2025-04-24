from .models import Project, Task, User
from rest_framework import serializers


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role", "date_joined")
        read_only_fields = ["id", "date_joined"]
        write_only_fields = ["password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key != "password":
                setattr(instance, key, value)
        if validated_data.get("password"):
            password = validated_data.pop("password")
            instance.set_password(password)
        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        members = validated_data.pop("members")
        project = Project.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        project.save()
        for member in members:
            project.members.add(member)
        project.save()
        return project


class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "status",
            "priority",
            "project_id",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        members = validated_data.pop("members")
        task = Task.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        task.save()
        return task
