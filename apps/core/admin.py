from django.contrib import admin  # <-- C'est cette ligne qui manque !
from django.shortcuts import redirect
from django.urls import reverse
from .models import SiteSettings, Banner, SocialLink

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone_primary', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        # Bloque le bouton "Ajouter" si une config existe déjà
        return not SiteSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        """ 
        Si une config existe, au lieu de voir la liste vide ou l'erreur,
        on est redirigé directement vers la page de modification.
        """
        obj = SiteSettings.objects.first()
        if obj:
            return redirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context)