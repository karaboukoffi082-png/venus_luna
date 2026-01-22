from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Wishlist

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("image", "alt_text", "is_main", "order")
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    ordering = ("order", "name")
    list_editable = ("order",) # Permet de changer l'ordre sans ouvrir la catégorie

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Ajout de 'display_image' pour voir le produit d'un coup d'œil
    list_display = (
        "display_image", 
        "name",
        "category",
        "price",
        "stock",
        "is_active",
        "featured",
    )
    # Rendre les champs modifiables directement dans la liste
    list_editable = ("price", "stock", "is_active", "featured")
    
    list_filter = ("is_active", "featured", "category")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    readonly_fields = ("created_at", "updated_at")

    # Fonction pour afficher la petite image dans la liste
    def display_image(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image and main_image.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', main_image.image.url)
        return "🖼️"
    display_image.short_description = "Aperçu"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_preview", "is_main", "order", "created_at")
    list_filter = ("is_main",)
    search_fields = ("product__name", "alt_text")
    ordering = ("product", "order")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu"

# On enregistre aussi la Wishlist pour pouvoir la voir
admin.site.register(Wishlist)