# filepath: c:\xampp\site_spirituel\apps\blog\admin.py
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste des articles
    list_display = ('title', 'author', 'published', 'created_at', 'updated_at')
    
    # Filtres rapides sur le côté droit
    list_filter = ('published', 'created_at', 'author')
    
    # Champs sur lesquels la barre de recherche fonctionne
    search_fields = ('title', 'content')
    
    # Génère automatiquement le slug pendant que tu tapes le titre dans l'admin
    prepopulated_fields = {'slug': ('title',)}
    
    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        ("Contenu de l'article", {
            'fields': ('title', 'slug', 'author', 'image', 'content')
        }),
        ("Paramètres de publication", {
            'fields': ('published',),
        }),
        ("Dates (Lecture seule)", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Masque cette section par défaut
        }),
    )
    
    # Empêche de modifier les dates manuellement
    readonly_fields = ('created_at', 'updated_at')

    # Optionnel : définit l'auteur par défaut sur l'utilisateur connecté
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)