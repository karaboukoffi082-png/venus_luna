from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Banner, SiteSettings, SocialLink
# Importez le formulaire de contact (vérifiez bien le chemin vers votre dossier contact)
from apps.contact.forms import ContactForm 

def home(request):
    """
    Page d'accueil avec bannières actives.
    """
    banners = Banner.objects.filter(is_active=True).order_by('order', '-created_at')
    site_settings = SiteSettings.get_solo()
    social_links = SocialLink.objects.all()
    context = {
        'banners': banners,
        'site_settings': site_settings,
        'social_links': social_links,
    }
    return render(request, 'pages/home.html', context)

def about(request):
    return render(request, 'pages/about.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def contact_view(request):
    """
    Vue pour gérer le formulaire de contact.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été transmis avec succès.")
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})


def about(request):
    return render(request, 'pages/about.html')

def confidentialite(request):
    return render(request, 'pages/confidentialite.html')

def faq(request):
    return render(request, 'pages/faq.html')

def custom_404(request, exception):
    return render(request, 'pages/404.html', status=404)