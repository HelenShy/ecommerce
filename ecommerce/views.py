from django.shortcuts import render

from .forms import ContactForm


def home_page(request):
    context= {}
    if request.user.is_authenticated:
        context['premium'] = "Secret"
    return render(request, 'home.html', context)


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    context = {'form': form}
    return render(request, 'contact/contact.html', context)
