from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingAddress, ShippingZone

# --- INLINES ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('line_total_display',)
    fields = ('product', 'name', 'price', 'quantity', 'line_total_display')
    extra = 0 

    def line_total_display(self, obj):
        return format_html('<b style="color: #001524;">{} F</b>', obj.line_total)
    line_total_display.short_description = "Sous-total"

class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    can_delete = False
    verbose_name_plural = 'Adresse de livraison'
    fields = ('full_name', 'phone', 'address', 'city')

# --- ADMIN MODELS ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # CORRECTION : Ajout de 'status' pour permettre list_editable
    list_display = (
        'id', 
        'status',           # Champ modifiable
        'colored_status',   # Aperçu visuel
        'status_stock', 
        'payment_indicator', 
        'total_display', 
        'view_receipt_link', 
        'created_at'
    )
    
    list_filter = ('status', 'payment_status', 'stock_updated', 'created_at')
    search_fields = ('id', 'email', 'user__username', 'shipping_address__full_name', 'shipping_address__phone')
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('user', 'email', 'status', 'notes')
        }),
        ('Détails Financiers', {
            'fields': ('subtotal', 'shipping_price', 'total'),
            'description': 'Les montants sont en FCFA (sans centimes).'
        }),
        ('Paiement & Suivi BKAPAY', {
            'fields': ('payment_status', 'payment_method', 'paygate_tx_id', 'payment_url', 'receipt', 'stock_updated'),
            'classes': ('collapse',) 
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'total', 'stock_updated', 'payment_url')
    
    # Doit figurer dans list_display pour fonctionner
    list_editable = ('status',) 
    
    inlines = (OrderItemInline, ShippingAddressInline)

    # --- MÉTHODES D'AFFICHAGE ---

    def colored_status(self, obj):
        colors = {
            'pending': '#ffc107',   # Jaune
            'paid': '#28a745',      # Vert
            'shipped': '#17a2b8',   # Bleu
            'delivered': '#001524', # Sombre
            'cancelled': '#dc3545',  # Rouge
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display().upper()
        )
    colored_status.short_description = "Aperçu"

    def payment_indicator(self, obj):
        if obj.payment_status:
            return format_html('<span style="color: #28a745;">✔ Payé</span>')
        if obj.payment_url:
            return format_html('<a href="{}" target="_blank" style="color: #d4af37;">🔗 Lien envoyé</a>', obj.payment_url)
        return format_html('<span style="color: #dc3545;">✘ Non payé</span>')
    payment_indicator.short_description = "Paiement"

    def total_display(self, obj):
        return format_html('<b style="color: #d4af37;">{} F</b>', obj.total)
    total_display.short_description = "Total"

    def status_stock(self, obj):
        if obj.stock_updated:
            return format_html('<span title="Stock déduit" style="cursor:help;">✅</span>')
        if obj.status == 'paid':
            return format_html('<span title="Stock non déduit !" style="cursor:help;">⚠️</span>')
        return format_html('<span style="color: #ccc;">-</span>')
    status_stock.short_description = "Stk"

    def view_receipt_link(self, obj):
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank" style="background: #001524; color: #d4af37; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 10px;">PDF</a>',
                obj.receipt.url
            )
        return "-"
    view_receipt_link.short_description = "Reçu"

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_display', 'delivery_time')
    list_editable = ('delivery_time',)

    def price_display(self, obj):
        return f"{obj.price} F"
    price_display.short_description = "Frais"