from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    # Le nouveau lien pour Démarché
    path('webhook/demarche/', views.demarche_webhook, name='demarche_webhook'),
    path('history/', views.order_history, name='order_history'),
    path('receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),
]