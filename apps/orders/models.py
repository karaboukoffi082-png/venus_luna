from django.conf import settings
from django.db import models
from django.utils import timezone

ORDER_STATUS = (
    ('pending', 'En attente de paiement'),
    ('paid', 'Payé (À préparer)'),
    ('processing', 'En cours de traitement'),
    ('shipped', 'Expédié'),
    ('delivered', 'Livré'),
    ('cancelled', 'Annulé'),
)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    email = models.EmailField("Email client", blank=True)
    status = models.CharField("Statut", max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Passage à 0 décimales pour le FCFA (plus propre pour Bkapay)
    subtotal = models.DecimalField("Sous-total", max_digits=10, decimal_places=0, default=0)
    shipping_price = models.DecimalField("Frais de port", max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField("Total", max_digits=10, decimal_places=0, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField("Notes", blank=True)

    # --- Champs Paiement Bkapay ---
    payment_status = models.BooleanField("Paiement confirmé", default=False)
    paygate_tx_id = models.CharField("ID Transaction Bkapay", max_length=100, blank=True, null=True, unique=True)
    payment_url = models.URLField("Lien de paiement", max_length=500, blank=True, null=True) # Nouveau : pour retrouver le lien
    payment_method = models.CharField("Méthode (Moov/TMoney)", max_length=50, blank=True, null=True)
    
    receipt = models.FileField("Reçu PDF", upload_to='receipts/%Y/%m/%d/', blank=True, null=True)
    stock_updated = models.BooleanField("Stock mis à jour", default=False, editable=False)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} — {self.get_status_display()}"

    def recalc_total(self, save=True):
        """ Calcule le sous-total et le total final """
        shipping = self.shipping_price or 0
        # Calcul du sous-total basé sur les items
        self.subtotal = sum([item.line_total for item in self.items.all()])
        self.total = self.subtotal + shipping
        if save:
            # On utilise update_fields pour ne pas déclencher inutilement d'autres signaux
            super().save(update_fields=['subtotal', 'total'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField("Nom du produit", max_length=255)
    price = models.DecimalField("Prix unitaire", max_digits=10, decimal_places=0, null=True, blank=True)
    quantity = models.PositiveIntegerField("Quantité", default=1)
    
    @property
    def line_total(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity

    def __str__(self):
        return f"{self.name} x{self.quantity}"

class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, related_name='shipping_address', on_delete=models.CASCADE)
    full_name = models.CharField("Nom complet", max_length=255)
    phone = models.CharField("Téléphone", max_length=50, blank=True)
    address = models.TextField("Adresse")
    city = models.CharField("Ville", max_length=150, blank=True)
    country = models.CharField("Pays", max_length=100, default="Togo")

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"

class ShippingZone(models.Model):
    name = models.CharField("Quartier / Zone", max_length=100)
    price = models.DecimalField("Frais de livraison", max_digits=10, decimal_places=0)
    delivery_time = models.CharField("Délai estimé", max_length=100, default="24h")

    class Meta:
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"