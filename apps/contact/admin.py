from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'body']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'subject', 'body', 'user', 'created_at']

    def has_add_permission(self, request):
        return False # On ne crée pas de messages depuis l'admin