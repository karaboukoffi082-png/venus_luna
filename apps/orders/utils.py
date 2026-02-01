import io
import logging
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives # Plus robuste pour HTML + Plain Text
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from xhtml2pdf import pisa 

from apps.products.models import Product

logger = logging.getLogger(__name__)

def generate_order_pdf(order):
    """ Génère le contenu binaire d'un PDF à partir du template HTML du reçu. """
    try:
        template = get_template('orders/pdf_receipt.html')
        # On passe les items explicitement pour faciliter le rendu du template
        context = {
            'order': order,
            'items': order.items.all(),
            'STATIC_ROOT': settings.STATIC_ROOT # Utile si tu as des images/logos dans le PDF
        }
        html = template.render(context)
        
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            return result.getvalue()
        return None
    except Exception as e:
        logger.error(f"Erreur génération PDF commande {order.id}: {str(e)}")
        return None

def send_order_confirmation(order):
    """ Envoie un email de confirmation avec le reçu PDF en pièce jointe. """
    subject = f'Confirmation de votre commande #{order.id} - Éveil Spirituel'
    recipient_email = order.email if order.email else (order.user.email if order.user else None)
    
    if not recipient_email:
        logger.error(f"Email non trouvé pour la commande {order.id}")
        return

    # Préparation du contenu
    context = {'order': order}
    html_content = render_to_string('emails/order_confirmation.html', context)
    text_content = strip_tags(html_content)
    
    try:
        # Utilisation de EmailMultiAlternatives pour une meilleure compatibilité
        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            settings.DEFAULT_FROM_EMAIL, 
            [recipient_email]
        )
        msg.attach_alternative(html_content, "text/html")
        
        # On attache le reçu si existant
        if order.receipt:
            # On s'assure de lire le fichier depuis le début
            order.receipt.open('rb') 
            msg.attach(f"Recu_Commande_{order.id}.pdf", order.receipt.read(), "application/pdf")
            order.receipt.close()
        
        msg.send()
        print(f"EMAIL : Confirmation envoyée pour la commande #{order.id}")
        
    except Exception as e:
        logger.error(f"Erreur envoi email commande {order.id}: {str(e)}")

# --- GESTION DU PANIER (Reste identique à ton code) ---
# --- GESTION DU PANIER ---

def get_cart(request):
    return request.session.get("cart", {})

def add_to_cart(request, product_id, quantity=1):
    cart = request.session.get("cart", {})
    p_id = str(product_id)
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        qty = 1

    if p_id in cart:
        if isinstance(cart[p_id], dict):
            cart[p_id]["quantity"] += qty
        else:
            cart[p_id] = {"quantity": qty}
    else:
        cart[p_id] = {"quantity": qty}

    request.session["cart"] = cart
    request.session.modified = True

def cart_items_detail(request):
    from apps.products.models import Product
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")
    for p_id, data in cart.items():
        try:
            product = Product.objects.get(pk=p_id)
            qty = data["quantity"] if isinstance(data, dict) else data
            sub = product.price * int(qty)
            total += sub
            items.append({"product": product, "quantity": qty, "subtotal": sub})
        except:
            continue
    return items, total

# VÉRIFIE BIEN CETTE FONCTION :
def update_cart_item(request, product_id, quantity):
    """ Met à jour la quantité ou supprime si <= 0 """
    cart = request.session.get("cart", {})
    p_id = str(product_id)
    if p_id in cart:
        try:
            qty = int(quantity)
            if qty > 0:
                cart[p_id]["quantity"] = qty
            else:
                del cart[p_id]
        except (ValueError, TypeError):
            pass
    request.session["cart"] = cart
    request.session.modified = True

def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True