# filepath: c:\xampp\site_spirituel\apps\accounts\admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Détails du Profil (Image, Tel, Adresse)'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
    # Désactive la création manuelle d'utilisateurs par l'admin
    def has_add_permission(self, request):
        return False

    # Autorise la suppression
    def has_delete_permission(self, request, obj=None):
        return True

# Réenregistrement du modèle User standard avec notre configuration
admin.site.unregister(User)
admin.site.register(User, UserAdmin)