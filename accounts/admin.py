from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # What fields to show in the list view
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'phone')
    
    # Filtering options on the right sidebar
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    # Searching capabilities
    search_fields = ('email', 'username', 'phone')
    ordering = ('email',)

    # Categorizing the fields in the detail/edit view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role Management', {'fields': ('role',)}),
    )
    
    # Fields to show when creating a new user in the admin panel
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'role', 'phone')}),
    )

    readonly_fields = ('last_login', 'date_joined')
