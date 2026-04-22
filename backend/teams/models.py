from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.name
    

class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('member', 'Member'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    class Meta:
        unique_together = ('team', 'user')


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    xp_awarded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "title"], name="unique_project_title_per_team"),
        ]

    def __str__(self):
        return self.title
    

class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('doing', 'Doing'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    deadline = models.DateField(null=True, blank=True)
    priority_points = models.PositiveIntegerField(default=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_project_tasks')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_project_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_project_tasks')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "title"], name="unique_project_task_title_per_project"),
        ]

    def __str__(self):
        return self.title


class JoinRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('team', 'Team'),
        ('project', 'Project'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # The user sending the join request
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    
    # Target team/project
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='join_requests')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='join_requests')
    
    # Optional message from requester
    message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('requester', 'project'), ('requester', 'team')]

    def __str__(self):
        target = self.team.name if self.team else self.project.title
        return f"{self.requester.username} requested to join {target} ({self.status})"

    @property
    def target_title(self):
        return self.team.name if self.team else self.project.title

    @property
    def target_creator(self):
        return self.team.creator if self.team else self.project.created_by


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    # The user sending the invitation (team owner/member)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    
    # The user receiving the invitation
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    
    # Target team/project. A project invite grants access through the project's team.
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='invitations')
    
    # Status of invitation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Optional message from inviter
    message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['inviter', 'invitee', 'team', 'project'],
                name='unique_invitation_project_target',
            ),
        ]

    def __str__(self):
        target = self.project.title if self.project else self.team.name
        return f"{self.inviter.username} invited {self.invitee.username} to {target} ({self.status})"

