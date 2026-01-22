from django import forms
from .models import Message

class ContactForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'email', 'subject', 'body']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Votre nom complet'}),
            'email': forms.EmailInput(attrs={'placeholder': 'votre@email.com'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Sujet de votre demande'}),
            'body': forms.Textarea(attrs={'placeholder': 'Comment pouvons-nous vous aider ?', 'rows': 5}),
        }