from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactForm(forms.Form):
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


class LoginForm(forms.Form):
    name = forms.CharField(label='Your name')
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    name = forms.CharField(label='Your name')
    email = forms.EmailField(label='Your email', required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_name(self):
        username = self.cleaned_data.get('name')
        qs = User.objects.filter(username=name)
        if qs.exists:
            raise forms.ValidationError('User already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists:
            raise forms.ValidationError('Email is taken')
        return username

    def clean(self):
        data = self.cleaned_data
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise forms.ValidationError('Passwords must match')
        return data
