from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserProfileForm(forms.ModelForm):
    # Champs additionnels venant du modèle Profile
    phone = forms.CharField(
        label="Téléphone (WhatsApp)", 
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+228...', 'class': 'form-control'})
    )
    address = forms.CharField(
        label="Quartier / Précisions livraison", 
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Si l'utilisateur a déjà un profil, on pré-remplit les champs phone et address
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone
            self.fields['address'].initial = self.instance.profile.address

        # Extrait de la méthode save dans UserProfileForm
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.phone = self.cleaned_data.get('phone')
                profile.address = self.cleaned_data.get('address')
                # L'image n'est mise à jour que si un nouveau fichier est fourni
                if self.cleaned_data.get('avatar'):
                    profile.avatar = self.cleaned_data.get('avatar')
                profile.save()
        return user  