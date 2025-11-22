from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# Unregister default User admin
admin.site.unregister(User)

# Register new User admin with profile inline
admin.site.register(User, CustomUserAdmin)

# Register your models here.
