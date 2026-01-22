# apps/blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'  # indispensable si tu utilises namespace='blog' dans config/urls.py

urlpatterns = [
    path('', views.index, name='list'),  # page d'accueil du blog
    path('<int:post_id>/', views.detail, name='detail'),  # détail d'un article
]
