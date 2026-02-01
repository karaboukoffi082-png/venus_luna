from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingAddress, ShippingZone

# --- INLINES ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('line_total',) # 'name', 'price', 'quantity' ne doivent être readonly que si tu veux bloquer l'édition
    fields = ('product', 'name', 'price', 'quantity', 'line_total')
    extra = 1

    def line_total(self, obj):
        # Affiche le total de la ligne avec l'unité
        return format_html("<b>{} F</b>", obj.line_total)
    line_total.short_description = "Sous-total"

class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    can_delete = False
    verbose_name_plural = 'Adresse de livraison'

# --- ADMIN MODELS ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'status_stock', 'payment_status', 
        'subtotal', 'shipping_price', 'total', 
        'view_receipt_link', 'created_at'
    )
    
    list_filter = ('status', 'payment_status', 'stock_updated', 'created_at')
    search_fields = ('id', 'email', 'user__username', 'shipping_address__full_name')
    
    fieldsets = (
        ('Informations Générales', {'fields': ('user', 'email', 'status', 'notes')}),
        ('Détails Financiers', {
            'fields': ('subtotal', 'shipping_price', 'total'),
            'description': 'Le total est calculé automatiquement après enregistrement.'
        }),
        ('Paiement & Sécurité', {'fields': ('payment_status', 'payment_method', 'paygate_tx_id', 'receipt', 'stock_updated')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'total', 'stock_updated')
    list_editable = ('status',)
    inlines = (OrderItemInline, ShippingAddressInline)

    def status_stock(self, obj):
        if obj.stock_updated:
            return format_html('<b style="color: #28a745;">{}</b>', "✔ Mis à jour")
        if obj.status == 'paid' and not obj.stock_updated:
            return format_html('<b style="color: #dc3545;">{}</b>', "✘ Erreur Auto")
        return format_html('<span style="color: #6c757d;">{}</span>', "En attente")
    status_stock.short_description = "Stock"

    def view_receipt_link(self, obj):
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank" style="color: #d4af37; font-weight: bold;">📄 Voir PDF</a>',
                obj.receipt.url
            )
        return format_html('<span style="color: #999;">{}</span>', "Pas de reçu")
    view_receipt_link.short_description = "Reçu PDF"

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'delivery_time')
    list_editable = ('price', 'delivery_time')