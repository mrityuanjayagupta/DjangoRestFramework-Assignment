from .models import Project, Task, User, Comment
from rest_framework import serializers


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "date_joined", "password"]
        read_only_fields = ["id", "date_joined"]

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
        fields = "__all__"
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
        fields = "__all__"
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        task = Task.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        task.save()
        return task


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "author", "created_at"]

    def create(self, validated_data):
        comment = Comment.objects.create(
            author=self.context["request"].user, **validated_data
        )
        comment.save()
        return comment
