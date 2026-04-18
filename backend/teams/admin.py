from django.contrib import admin
from .models import Team, TeamMember, Project, ProjectTask

admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Project)
admin.site.register(ProjectTask)