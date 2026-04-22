from django.contrib import admin
from .models import Team, TeamMember, Project, ProjectTask, JoinRequest, Invitation

admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Project)
admin.site.register(ProjectTask)
admin.site.register(JoinRequest)
admin.site.register(Invitation)
