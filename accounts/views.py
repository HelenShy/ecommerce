from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.http import is_safe_url

from .forms import LoginForm, RegisterForm


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {'form': form}
    next_get = request.GET.get('next', None)
    next_post = request.POST.get('next', None)
    next = next_get or next_post
    if form.is_valid():
        username = form.cleaned_data.get('name')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            print(request.user.is_authenticated)
            login(request, user)
            if is_safe_url(next):
                return redirect(next)
            return redirect('/login')
        else:
            print("Error")
    return render(request, 'accounts/login.html', context)


def register_page(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def logout_page(request):
    logout(request)
    return redirect('/')
