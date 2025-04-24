from django.contrib import admin
from .models import Project, Task, User, Comment


class UserDjangoAdmin(admin.ModelAdmin):
    readonly_fields = ("date_joined",)


admin.site.register(User, UserDjangoAdmin)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)
