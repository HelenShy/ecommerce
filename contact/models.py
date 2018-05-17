from django.db import models
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings


class Contact(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255)
    message = models.CharField(max_length=120, blank=True, null=True)

    def send_mail(self):
        """
        Sends filled contact form to site`s admin.
        """
        context = {
            'name': self.name,
            'email': self.email,
            'message': self.message
        }
        txt_ = get_template('contact/emails/contact-form.txt').render(context)
        html_ = get_template('contact/emails/contact-form.html').render(context)

        subject = 'Contact form sent from BookShop site'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipients_list = [settings.DEFAULT_FROM_EMAIL]
        sent_mail = send_mail(
            subject,
            txt_,
            from_email,
            recipients_list,
            html_message=html_,
            fail_silently=False
        )
        print(sent_mail)
        return sent_mail
