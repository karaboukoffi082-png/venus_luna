from decimal import Decimal
from apps.products.models import Product
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_confirmation(order):
    subject = f'Confirmation de votre commande #{order.id} - Éveil Spirituel'
    
    # On crée le contenu HTML de l'email
    html_message = render_to_string('emails/order_confirmation.html', {'order': order})
    plain_message = strip_tags(html_message) # Version texte simple pour les vieux téléphones
    
    send_mail(
        subject,
        plain_message,
        'Éveil Spirituel <ton-email@gmail.com>',
        [order.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def get_cart(request):
    """
    Récupère le panier depuis la session
    """
    return request.session.get("cart", {})

def add_to_cart(request, product_id, quantity=1):
    cart = request.session.get("cart", {})
    p_id = str(product_id) # On force en string pour le JSON de la session

    if p_id in cart:
        # On vérifie que cart[p_id] est bien un dictionnaire
        if isinstance(cart[p_id], dict):
            cart[p_id]["quantity"] += quantity
        else:
            # Si c'était juste un chiffre (ancienne logique), on répare
            cart[p_id] = {"quantity": quantity}
    else:
        cart[p_id] = {"quantity": quantity}

    request.session["cart"] = cart
    request.session.modified = True

def cart_items_detail(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")

    for product_id, data in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
            # Sécurité : on vérifie si data est un dictionnaire ou un entier
            quantity = data["quantity"] if isinstance(data, dict) else data
            
            price = Decimal(str(product.price)) # Conversion propre pour calcul
            subtotal = price * quantity
            total += subtotal

            items.append({
                "product": product,
                "name": product.name,
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal,
            })
        except (Product.DoesNotExist, TypeError, KeyError):
            continue

    return items, total

def update_cart_item(request, product_id, quantity):
    """
    Met à jour la quantité d’un produit
    """
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        if quantity > 0:
            cart[product_id]["quantity"] = quantity
        else:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True


def clear_cart(request):
    """
    Vide complètement le panier
    """
    request.session["cart"] = {}
    request.session.modified = True


