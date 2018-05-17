from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib import messages

from .forms import ContactForm
from .models import Contact


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    context = {'form': form}

    return render(request, 'contact/contact.html', context)


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = '/'

    def form_valid(self, form):
        msg = """
        Thank you for your inquiry.
        We will respond as soon as possible generally within a few hours."""
        messages.success(self.request, msg)
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message =  form.cleaned_data.get('message')
        contact_mail=  Contact.objects.create(name=name, email=email,
                                                  message=message)
        contact_mail.send_mail()
        return super(ContactView, self).form_valid(form)
