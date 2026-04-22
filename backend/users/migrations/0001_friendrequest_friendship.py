# Generated for friend request and friendship support.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FriendRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("responded_at", models.DateTimeField(blank=True, null=True)),
                ("from_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_friend_requests", to=settings.AUTH_USER_MODEL)),
                ("to_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_friend_requests", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Friendship",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("user_one", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="friendships_as_user_one", to=settings.AUTH_USER_MODEL)),
                ("user_two", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="friendships_as_user_two", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="friendrequest",
            constraint=models.UniqueConstraint(fields=("from_user", "to_user"), name="unique_friend_request_direction"),
        ),
        migrations.AddConstraint(
            model_name="friendrequest",
            constraint=models.CheckConstraint(condition=~models.Q(from_user=models.F("to_user")), name="friend_request_users_must_differ"),
        ),
        migrations.AddConstraint(
            model_name="friendship",
            constraint=models.UniqueConstraint(fields=("user_one", "user_two"), name="unique_friendship_pair"),
        ),
        migrations.AddConstraint(
            model_name="friendship",
            constraint=models.CheckConstraint(condition=~models.Q(user_one=models.F("user_two")), name="friendship_users_must_differ"),
        ),
    ]
