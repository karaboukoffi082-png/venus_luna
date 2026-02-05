from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

# Import des modèles de l'application Core
from .models import Banner, SiteSettings, SocialLink

# Import des modèles des autres applications
from apps.products.models import Product, Category 
from apps.blog.models import Post
from apps.contact.forms import ContactForm 
def cgv_view(request):
    return render(request, 'pages/cgv.html') # Assure-toi que ce template existe
def home(request):
    """
    Vue unique de la page d'accueil.
    Regroupe les bannières, les produits, les catégories et les articles de blog.
    """
    # 1. Récupération des bannières actives
    banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # 2. Récupération des paramètres du site et liens sociaux
    site_settings = SiteSettings.get_solo()
    social_links = SocialLink.objects.all()
    
    # 3. Récupération des 6 derniers produits
    products = Product.objects.all().order_by('-created_at')[:6]
    
    # 4. Récupération de toutes les catégories pour le menu ou la grille
    categories = Category.objects.all()
    
    # 5. Récupération des 3 derniers articles de blog PUBLIÉS
    posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
    
    # Construction du contexte unique
    context = {
        'banners': banners,
        'site_settings': site_settings,
        'social_links': social_links,
        'products': products,
        'categories': categories,
        'posts': posts,
    }
    
    return render(request, 'pages/home.html', context)

def about(request):
    """Page À Propos"""
    return render(request, 'pages/about.html')

def contact_view(request):
    """Gestion du formulaire de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été transmis avec succès.")
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})

def confidentialite(request):
    """Page Politique de Confidentialité"""
    return render(request, 'pages/confidentialite.html')

def faq(request):
    """Page Foire Aux Questions"""
    return render(request, 'pages/faq.html')

def custom_404(request, exception):
    """Page d'erreur 404 personnalisée"""
    return render(request, 'pages/404.html', status=404)