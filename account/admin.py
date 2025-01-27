from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active')
    ordering = ('created_at',)
    readonly_fields = ("is_deleted","is_email_verified", "is_phone_verified")

admin.site.register(CustomUser, CustomUserAdmin)