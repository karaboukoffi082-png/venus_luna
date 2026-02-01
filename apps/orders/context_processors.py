from .utils import cart_items_detail

def cart_context(request):
    """
    Rend les données du panier disponibles dans tous les templates.
    """
    items, total = cart_items_detail(request)
    return {
        'cart_items': items,
        'cart_total': total, # Utilisé pour le récapitulatif
        'cart_count': sum(item['quantity'] for item in items) # Pour le badge de la navbar
    }