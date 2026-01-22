from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # --- Produits ---
    path('', views.product_list, name='list'), 
    path('produit/<int:pk>/', views.product_detail, name='detail'),
    path('ma-wishlist/', views.wishlist_detail, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    # --- Dashboard Admin ---
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]