from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import EmailActivation, GuestUser
from .signals import user_logged_in

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserDetailChangeForm(forms.ModelForm):
    """
    A form for users to update their profiles.
    """
    name = forms.CharField(label='Name', required=False)
    class Meta:
        model = User
        fields = ['name']


class GuestForm(forms.ModelForm):
    class Meta:
        model = GuestUser
        fields= ['email',]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self). __init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        print('0 save')
        obj = super(GuestForm, self).save(commit=False)
        print('1 save')
        if commit:
            obj.save()
            request = self.request
            request.session['guest_id'] = obj.id
            print('2 save')
        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self). __init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email  = data.get("email")
        password  = data.get("password")
        user_qs = User.objects.filter(email=email)
        user_inactive = user_qs.filter(is_active=False).exists()
        confirmation_mail_active = EmailActivation.objects.filter(
            email=email).confirmable()
        link = reverse('accounts:password_reset')
        if user_inactive:
            if confirmation_mail_active:
                msg = """
                Check your mail for confirmation letter. Or go to <a href='{link}'>
                to resend confirmation email</a>.""".format(link=link)
                raise forms.ValidationError(mark_safe(msg))
            else:
                msg = """
                Mail is not confirmed. Go to <a href='{link}'>
                resend confirmation email</a>.""".format(link=link)
                raise forms.ValidationError(mark_safe(msg))
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError(mark_safe("Invalid credentials"))
        login(request, user)
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session['guest_id']
        except:
            pass
        return data



class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('name', 'email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField

    def clean_email(self):
        email = self.cleand_data.get('email')
        if not EmailActivation.objects.email_exists(email).exists():
            link = reverse('register')
            msg = """
            This email does not exist. Would you like to <a href="{link}">
            register</a>?
            """.format(link=link)
            raise forms.ValidationError(mark_safe(msg))
        return email
