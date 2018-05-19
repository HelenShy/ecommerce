from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.views.generic.edit import CreateView, FormView, View, FormMixin, UpdateView
from django.views.generic import DetailView
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse

from .forms import (LoginForm,
                    RegisterForm,
                    GuestForm,
                    ReactivateEmailForm,
                    UserDetailChangeForm)
from .models import GuestUser, EmailActivation
from .mixins import NextUrlMixin, RequestAttachArgsMixin


class GuestRegisterView(RequestAttachArgsMixin, NextUrlMixin, CreateView):
    form_class = GuestForm
    default_next = '/register'

    def form_invalid(self, form):
        return redirect(self.default_next)

    def get_success_url(self):
        return self.redirect_path()


class LoginView(RequestAttachArgsMixin, NextUrlMixin, FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_next = '/'

    def form_valid(self, form):
        redirect_path = self.redirect_path()
        messages.success(self.request, 'Logged in succesfully.')
        return redirect(redirect_path)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

    def form_valid(self, form):
        super(RegisterView, self).form_valid(form)
        messages.success(self.request, 'Please check your email and confirm your account.')
        return redirect(self.success_url)


def logout_view(request):
    logout(request)
    messages.success(request, 'User log out.')
    return redirect("/")


class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'
    def get_object(self):
        return self.request.user


class EmailActivationView(FormMixin, View):
    success_url = '/login'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            qs_confirm = qs.confirmable()
            if qs_confirm.count() == 1:
                email_activation = qs.first()
                activation = email_activation.activate()
                messages.success(request, "Your account is activated. You can login.")
                return redirect('login')
            qs_activated = qs.filter(activated=True)
            if qs.exists():
                link = reverse('accounts:password_reset')
                msg = """
                Your email has already been confirmed. Do you need to <a href="{link}">
                reset your password</a>?
                """.format(link=link)
                messages.success(request, mark_safe(msg))
                return redirect('login')
        context = {'form': self.get_form(), 'key': key}
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = """Activation link sent. Please check your email."""
        messages.success(request, msg)
        email = form.cleaned_data.get('email')
        obj =  EmailActivation.objects.email_exists(email=email).first()
        email_activation=  EmailActivation.objects.create(user=obj.user, email=email)
        email_activation.send_activation()
        return super(EmailActivationView, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation-error.html', context)



class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/update_user_detail.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('account:home')
