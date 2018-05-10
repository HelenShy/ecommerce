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


# def guest_register_view(request):
#     form = GuestForm(request.POST or None)
#     context = {
#         "form": form
#     }
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#     if form.is_valid():
#         email       = form.cleaned_data.get("email")
#         new_guest_email = GuestUser.objects.create(email=email)
#         request.session['guest_id'] = new_guest_email.id
#         if is_safe_url(redirect_path, request.get_host()):
#             return redirect(redirect_path)
#         else:
#             return redirect("/register/")
#     return redirect("/register/")


class GuestRegisterView(RequestAttachArgsMixin, NextUrlMixin, CreateView):
    form_class = GuestForm
    default_next = '/register'

    # def form_valid(self, form):
    #     email = form.cleaned_data.get("email")
    #     new_guest_email = GuestUser.objects.create(email=email)
    #     return redirect(self.redirect_path())

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
        return redirect(redirect_path)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'


def logout_view(request):
    logout(request)
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
