from rest_framework import serializers
from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "user", "created_at"]
        read_only_fields = ["user", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    def validate_title(self, value):
        request = self.context.get("request")
        user = request.user if request else None
        queryset = Task.objects.filter(title__iexact=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if user is not None:
            queryset = queryset.filter(user=user)

        if queryset.exists():
            raise serializers.ValidationError("You already have a task with this title.")
        return value

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "status",
            "priority",
            "created_at",
            "user",
            "category",
            "category_name",
        ]
        read_only_fields = ["user", "created_at"]
