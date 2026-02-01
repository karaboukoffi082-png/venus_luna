import re
from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        label="Nom complet", 
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Jean Dossou'})
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )
    
    phone = forms.CharField(
        label="Téléphone (T-Money ou Moov)", 
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 90 01 02 03'})
    )
    
    address = forms.CharField(
        label="Adresse précise", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Quartier, repères...'})
    )
    
    city = forms.CharField(
        label="Ville", 
        max_length=150, 
        initial="Lomé",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # postal_code a été supprimé car absent de la table shippingaddress
    
    country = forms.CharField(
        label="Pays", 
        max_length=100, 
        initial="Togo",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        label="Notes pour la livraison (optionnel)", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ex: Préciser une heure de passage'}),
        required=False
    )

    def clean_phone(self):
        """Vérifie que le numéro est un numéro Togolais valide"""
        phone = self.cleaned_data.get('phone')
        clean_phone = re.sub(r'\D', '', phone)

        if clean_phone.startswith('228'):
            short_phone = clean_phone[3:]
        else:
            short_phone = clean_phone

        if len(short_phone) != 8:
            raise forms.ValidationError("Le numéro doit comporter 8 chiffres.")

        valid_prefixes = ('90', '91', '92', '93', '96', '97', '98', '99', '79', '70')
        if not short_phone.startswith(valid_prefixes):
            raise forms.ValidationError("Numéro T-Money ou Moov invalide.")

        return clean_phone