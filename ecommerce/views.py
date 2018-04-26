from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, RegisterForm, ContactForm


def home_page(request):
    context= {}
    if request.user.is_authenticated:
        context['premium'] = "Secret"
    return render(request, 'home.html', context)


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        username = form.cleaned_data.get('name')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            print(request.user.is_authenticated)
            login(request, user)
            return redirect('/login')
        else:
            print("Error")
    return render(request, 'auth/login.html', context)


def register_page(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    context = {'form': form}
    return render(request, 'auth/register.html', context)


def logout_page(request):
    logout(request)
    return redirect('/home')


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    context = {'form': form}
    return render(request, 'contact/contact.html', context)
