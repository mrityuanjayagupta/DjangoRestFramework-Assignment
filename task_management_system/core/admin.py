from django.contrib import admin
from .models import User


class UserDjangoAdmin(admin.ModelAdmin):
    list_display = ("date_joined",)
    readonly_fields = ("date_joined",)


admin.site.register(User, UserDjangoAdmin)
