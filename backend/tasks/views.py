from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer
from engagement.utils import award_xp, log_activity


class CategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TaskListCreateAPIView(ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        award_xp(self.request.user, 5)
        log_activity(
            actor=self.request.user,
            action_type="task_created",
            message=f'Task created: "{task.title}".',
            xp_change=5,
            task=task,
        )


class TaskDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_status = instance.status
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()

        if previous_status != "done" and instance.status == "done":
            award_xp(request.user, 10)
            log_activity(
                actor=request.user,
                action_type="task_completed",
                message=f'Task completed: "{instance.title}".',
                xp_change=10,
                task=instance,
            )

        return response
