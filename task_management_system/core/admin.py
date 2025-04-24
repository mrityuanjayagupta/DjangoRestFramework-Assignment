from django.contrib import admin
from .models import Project, User


class UserDjangoAdmin(admin.ModelAdmin):
    readonly_fields = ("date_joined",)


admin.site.register(User, UserDjangoAdmin)
admin.site.register(Project)
