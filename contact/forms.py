from django import forms
from django.contrib.auth import get_user_model

from .models import Contact


User = get_user_model()

class ContactForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter your name"
            })
        )
    email = forms.EmailField(
        widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Enter your email"
            })
        )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': "Enter your message"
                })
        )

    class Meta:
        model = Contact
        fields = ('name', 'email', 'message')
