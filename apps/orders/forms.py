from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=255)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Téléphone", max_length=50, required=False)
    address = forms.CharField(label="Adresse", widget=forms.Textarea)
    city = forms.CharField(label="Ville", max_length=150, required=False)
    postal_code = forms.CharField(label="Code postal", max_length=20, required=False)
    country = forms.CharField(label="Pays", max_length=100, required=False)
    notes = forms.CharField(label="Notes (optionnel)", widget=forms.Textarea, required=False)