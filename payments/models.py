# payments/models.py
from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("success", "Succès"),
        ("failed", "Échec"),
    )

    reference = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.status}"