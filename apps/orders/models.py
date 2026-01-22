from django.conf import settings
from django.db import models
from django.utils import timezone

# ORDER_STATUS : Définit les étapes de la commande
ORDER_STATUS = (
    ('pending', 'En attente'),
    ('processing', 'En cours'),
    ('shipped', 'Expédié'),
    ('delivered', 'Livré'),
    ('cancelled', 'Annulé'),
)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    email = models.EmailField("Email client", blank=True)
    status = models.CharField("Statut", max_length=20, choices=ORDER_STATUS, default='pending')
    total = models.DecimalField("Total", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} — {self.get_status_display()}"

    def recalc_total(self):
        total = sum([item.line_total for item in self.items.all()])
        self.total = total
        self.save(update_fields=['total'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # Référence directe par string pour éviter les imports circulaires
    product = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField("Nom du produit", max_length=255)
    price = models.DecimalField("Prix unitaire", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Quantité", default=1)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    @property
    def line_total(self):
        # On vérifie que price n'est pas None avant de calculer
        if self.price and self.quantity:
            return self.price * self.quantity
        return 0  # On retourne 0 par défaut pour éviter le crash

    def __str__(self):
        # Utilisation de self.order.id au lieu de order_id pour plus de clarté
        return f"{self.name} x{self.quantity} — Cmd #{self.order.id if self.order else 'N/A'}"
class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, related_name='shipping_address', on_delete=models.CASCADE)
    full_name = models.CharField("Nom complet", max_length=255)
    phone = models.CharField("Téléphone", max_length=50, blank=True)
    address = models.TextField("Adresse")
    city = models.CharField("Ville", max_length=150, blank=True)
    postal_code = models.CharField("Code postal", max_length=20, blank=True)
    country = models.CharField("Pays", max_length=100, default="Togo")

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"

    def __str__(self):
        return f"Livraison Cmd #{self.order_id} — {self.full_name}"

# --- CETTE CLASSE DOIT ÊTRE BIEN SORTIE DES AUTRES ---
class ShippingZone(models.Model):
    name = models.CharField("Quartier / Zone", max_length=100)
    price = models.DecimalField("Frais de livraison", max_digits=10, decimal_places=0)
    delivery_time = models.CharField("Délai estimé", max_length=100, default="24h - 48h")

    class Meta:
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"

    def __str__(self):
        return f"{self.name} ({self.price} F)"
