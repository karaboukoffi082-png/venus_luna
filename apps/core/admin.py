from django.contrib import admin
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
        """ Redirige vers la modification si une config existe déjà """
        obj = SiteSettings.objects.first()
        if obj:
            return redirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context)

# --- AJOUTE CES LIGNES POUR CORRIGER LES ERREURS 404 ---

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    ordering = ('order',)

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon_class')
    search_fields = ('name', 'url')