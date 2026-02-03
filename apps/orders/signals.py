from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.db.models import F
from .models import Order
from .utils import generate_order_pdf
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def handle_order_automation(sender, instance, created, **kwargs):
    """
    Gère les automations de stock et de PDF de manière atomique.
    Déclenché après le paiement réussi (via Webhook PayPlus).
    """
    
    # 1. LOGIQUE : COMMANDE PAYÉE (Déduction du stock + PDF)
    if instance.status == 'paid' and not instance.stock_updated:
        try:
            # A. Génération du PDF si absent
            if not instance.receipt:
                pdf_content = generate_order_pdf(instance)
                if pdf_content:
                    filename = f"recu_venus_luna_{instance.id}.pdf"
                    instance.receipt.save(filename, ContentFile(pdf_content), save=False)

            # B. Mise à jour des stocks (Utilisation de F pour la sécurité)
            for item in instance.items.all():
                if item.product and hasattr(item.product, 'stock'):
                    item.product.stock = F('stock') - item.quantity
                    item.product.save(update_fields=['stock'])

            # C. Validation de l'automation
            # On utilise update() ici pour éviter de redéclencher le signal post_save à l'infini
            Order.objects.filter(id=instance.id).update(
                stock_updated=True,
                # Si le PDF a été ajouté à l'instance au-dessus, on l'enregistre ici
                # Note: si receipt.save a été utilisé sans save=False, c'est déjà en DB
            )
            
            # On sauvegarde le champ receipt séparément car update() ne gère pas bien les fichiers
            if instance.receipt:
                instance.save(update_fields=['receipt'])

            logger.info(f"SUCCESS: Stock déduit et PDF généré pour la commande #{instance.id}")
            
        except Exception as e:
            logger.error(f"ERROR: Echec de l'automation pour la commande #{instance.id}: {e}")

    # 2. LOGIQUE : ANNULATION (Ré-incrémentation du stock)
    elif instance.status == 'cancelled' and instance.stock_updated:
        try:
            for item in instance.items.all():
                if item.product and hasattr(item.product, 'stock'):
                    item.product.stock = F('stock') + item.quantity
                    item.product.save(update_fields=['stock'])
            
            Order.objects.filter(id=instance.id).update(stock_updated=False)
            logger.info(f"CANCEL: Commande #{instance.id} annulée, stock rendu.")
            
        except Exception as e:
            logger.error(f"ERROR: Echec du retour de stock pour #{instance.id}: {e}")