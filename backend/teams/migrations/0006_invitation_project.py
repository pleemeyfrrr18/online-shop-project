# Generated for project invitation support.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0005_invitation"),
    ]

    operations = [
        migrations.AddField(
            model_name="invitation",
            name="project",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="invitations", to="teams.project"),
        ),
        migrations.AlterUniqueTogether(
            name="invitation",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.UniqueConstraint(fields=("inviter", "invitee", "team", "project"), name="unique_invitation_project_target"),
        ),
    ]
