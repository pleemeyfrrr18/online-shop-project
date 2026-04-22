# Generated for weighted project task progress.

from django.db import migrations, models


def normalize_priorities(apps, schema_editor):
    Project = apps.get_model("teams", "Project")
    for project in Project.objects.all():
        tasks = list(project.tasks.order_by("id"))
        if not tasks:
            continue
        if len(tasks) == 1:
            tasks[0].priority_points = 100
            tasks[0].save(update_fields=["priority_points"])
            continue

        total = sum(task.priority_points for task in tasks)
        if total <= 0:
            base = 100 // len(tasks)
            remainder = 100 - (base * len(tasks))
            for index, task in enumerate(tasks):
                task.priority_points = base + (1 if index < remainder else 0)
                task.save(update_fields=["priority_points"])
            continue

        scaled = []
        for task in tasks:
            exact = task.priority_points * 100 / total
            floor_value = int(exact)
            scaled.append((task, floor_value, exact - floor_value))

        remainder = 100 - sum(item[1] for item in scaled)
        scaled.sort(key=lambda item: item[2], reverse=True)
        for index, (task, floor_value, _fraction) in enumerate(scaled):
            task.priority_points = floor_value + (1 if index < remainder else 0)
            task.save(update_fields=["priority_points"])


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0006_invitation_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="status",
            field=models.CharField(choices=[("active", "Active"), ("finished", "Finished")], default="active", max_length=20),
        ),
        migrations.AddField(
            model_name="project",
            name="xp_awarded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="projecttask",
            name="completed_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="completed_project_tasks", to="auth.user"),
        ),
        migrations.AddField(
            model_name="projecttask",
            name="priority_points",
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.RunPython(normalize_priorities, migrations.RunPython.noop),
    ]
