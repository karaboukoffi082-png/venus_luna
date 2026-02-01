from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.db.models import F
from .models import Order
from .utils import generate_order_pdf

@receiver(post_save, sender=Order)
def handle_order_automation(sender, instance, created, **kwargs):
    """
    Gère les automations de stock et de PDF.
    Utilise 'stock_updated' pour garantir l'idempotence.
    """
    
    # 1. LOGIQUE : COMMANDE PAYÉE (Déduction du stock + PDF)
    if instance.status == 'paid' and not instance.stock_updated:
        # A. Génération du PDF si absent
        if not instance.receipt:
            pdf_content = generate_order_pdf(instance)
            if pdf_content:
                filename = f"recu_spirituel_cmd_{instance.id}.pdf"
                instance.receipt.save(filename, ContentFile(pdf_content), save=False)

        # B. Mise à jour des stocks
        for item in instance.items.all():
            if item.product and hasattr(item.product, 'stock'):
                item.product.stock = F('stock') - item.quantity
                item.product.save(update_fields=['stock'])

        # C. Validation de l'automation
        instance.stock_updated = True
        # On sauvegarde les deux champs d'un coup
        instance.save(update_fields=['receipt', 'stock_updated'])
        print(f"AUTOMATION : Stock déduit et PDF généré pour #{instance.id}")

    # 2. LOGIQUE : ANNULATION (Ré-incrémentation du stock)
    elif instance.status == 'cancelled' and instance.stock_updated:
        # On ne rend le stock QUE si il avait été déduit auparavant
        for item in instance.items.all():
            if item.product and hasattr(item.product, 'stock'):
                item.product.stock = F('stock') + item.quantity
                item.product.save(update_fields=['stock'])
        
        # On remet le marqueur à False car le stock est revenu à l'état initial
        instance.stock_updated = False
        instance.save(update_fields=['stock_updated'])
        print(f"AUTOMATION : Commande #{instance.id} annulée, stock ré-incrémenté.")