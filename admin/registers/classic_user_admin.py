from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from django_classic.models import ClassicSystemUser


# Register your models here.
@admin.register(ClassicSystemUser)
class ClassicSystemUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ['username', 'first_name', 'last_name', 'phone', 'email', 'is_staff', 'is_active', ]
    list_display_links = ['username', ]
    search_fields = ['username', 'first_name', 'last_name']

    # form = ApplicationSlipForm
