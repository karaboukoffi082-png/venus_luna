from decimal import Decimal
from apps.products.models import Product

# Identifiant unique de la session pour le panier
CART_SESSION_ID = 'cart'

def get_cart(request):
    """
    Récupère le panier depuis la session.
    """
    return request.session.get(CART_SESSION_ID, {})

def save_cart(request, cart):
    """
    Sauvegarde le panier dans la session et marque la session comme modifiée.
    """
    request.session[CART_SESSION_ID] = cart
    request.session.modified = True

def add_to_cart(request, product_id, quantity=1):
    """
    Ajoute un produit au panier ou incrémente sa quantité.
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if isinstance(cart[product_id_str], dict):
            cart[product_id_str]['quantity'] += quantity
        else:
            # Réparation si les données étaient mal formatées
            product = Product.objects.get(id=product_id)
            cart[product_id_str] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
            }
    else:
        product = Product.objects.get(id=product_id)
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
        }
    save_cart(request, cart)

def update_cart_item(request, product_id, quantity):
    """
    Met à jour la quantité d'un produit. Supprime l'article si quantité <= 0.
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if quantity > 0:
            cart[product_id_str]['quantity'] = quantity
        else:
            cart.pop(product_id_str)
        save_cart(request, cart)

def clear_cart(request):
    """
    Vide complètement le panier (utilisé après succès PayGate).
    """
    save_cart(request, {})

def cart_items_detail(request):
    """
    Retourne la liste détaillée des produits pour l'affichage et le PDF.
    """
    cart = get_cart(request)
    items = []
    total = Decimal('0.00')
    
    for product_id_str, item in cart.items():
        product = Product.objects.filter(id=int(product_id_str)).first()
        if not product:
            continue
            
        # On utilise le prix actuel du produit en base pour plus de sécurité
        price = Decimal(str(product.price))
        quantity = item['quantity']
        line_total = price * quantity
        total += line_total
        
        items.append({
            'product': product,
            'name': product.name,
            'price': price,
            'quantity': quantity,
            'line_total': line_total,
            'subtotal': line_total, 
        })
        
    return items, total