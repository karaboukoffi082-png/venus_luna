from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, ShippingZone

# Permet de voir les produits d'une commande directement dans la fiche commande
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('name', 'price', 'quantity', 'line_total')
    extra = 0

    def line_total(self, obj):
        return obj.line_total
    line_total.short_description = "Sous-total"

# Permet de voir l'adresse de livraison directement dans la fiche commande
class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    can_delete = False
    verbose_name_plural = 'Adresse de livraison'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 'status' est mis en 'list_editable' pour changer l'état (Payé, Expédié...) sans ouvrir la fiche
    list_display = ('id', 'user', 'email', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'email', 'user__username', 'shipping_address__full_name')
    readonly_fields = ('created_at', 'updated_at', 'total')
    list_editable = ('status',)
    inlines = (OrderItemInline, ShippingAddressInline)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'city', 'phone')
    search_fields = ('full_name', 'address', 'phone')

# --- NOUVEAU : Gestion des quartiers de Lomé ---
@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'delivery_time')
    list_editable = ('price', 'delivery_time')
    search_fields = ('name',)