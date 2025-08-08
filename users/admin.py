from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import *  # Import your custom form


from .models import *

class CustomUserAdmin(UserAdmin):
   
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('mobile', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('mobile', 'email', 'password', 'firebase_uid')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_verified')}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_verified')}
        ),
    )

    search_fields = ('mobile',)
    ordering = ('mobile',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserCredit)
admin.site.register(UserKYC)