from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('a-propos/', views.about, name='about'),      # <--- AJOUTER CECI
    path('confidentialite-et-conditions/', views.confidentialite, name='privacy'),
    path('foire-aux-questions/', views.faq, name='faq'), # <--- AJOUTER CECI

]
