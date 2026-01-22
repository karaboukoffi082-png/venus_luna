from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User

# On ne réimporte pas Product ici car nous sommes dans le même fichier.

def upload_to_product_path(instance, filename):
    now = timezone.now()
    return f'products/{instance.__class__.__name__.lower()}/{now:%Y/%m}/{filename}'

class Category(models.Model):
    name = models.CharField("Nom", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    order = models.PositiveIntegerField("Ordre", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:list') + f'?category={self.slug}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:180]
            slug = base
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField("Nom", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, blank=True)
    short_description = models.CharField("Courte description", max_length=255, blank=True)
    description = models.TextField("Description", blank=True)
    price = models.DecimalField("Prix", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    compare_price = models.DecimalField("Prix barré", max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField("Publié / Disponible", default=True)
    stock = models.IntegerField("Stock", default=0)
    featured = models.BooleanField("Mis en avant", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.id])

    def available(self):
        return self.is_active and (self.stock is None or self.stock > 0)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:220]
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Image", upload_to=upload_to_product_path)
    alt_text = models.CharField("Texte alternatif", max_length=255, blank=True)
    is_main = models.BooleanField("Image principale", default=False)
    order = models.PositiveSmallIntegerField("Ordre", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image produit"
        verbose_name_plural = "Images produit"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image {self.id} — {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

# ET POUR TON AUTRE FICHIER (ShippingZone dans orders/models.py) :
class ShippingZone(models.Model):
    name = models.CharField("Quartier / Zone", max_length=100)
    price = models.DecimalField("Frais de livraison", max_digits=10, decimal_places=0)
    delivery_time = models.CharField("Délai estimé", max_length=100, default="24h - 48h")

    def __str__(self):
        return f"{self.name} ({self.price} F)"