from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.http import is_safe_url
from django.views.generic.edit import CreateView

from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestUser


class LoginView(CreateView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'

    def is_valid(self, form):
        request = self.request
        next_get = request.GET.get('next', None)
        next_post = request.POST.get('next', None)
        next = next_get or next_post

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            if request.session.get('guest_id', None):
                del request.session['guest_id']
            login(request, user)
            if is_safe_url(next, request.get_host()):
                return redirect(next)
            return redirect('/login')
        return super(LoginView, self).form_invalid()


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'



def guest_register_page(request):
    form = GuestForm(request.POST or None)
    next_get = request.GET.get('next', None)
    next_post = request.POST.get('next', None)
    next = next_get or next_post
    if form.is_valid():
        email = form.cleaned_data.get('email')
        guest, guest_created = GuestUser.objects.get_or_create(email=email)
        request.session['guest_id'] = guest.id
        if is_safe_url(next, request.get_host()):
            return redirect(next)
        return redirect('/register')
    return redirect('/register')
