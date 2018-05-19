from django.shortcuts import render, redirect
from django.conf import settings
import stripe
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from .models import BillingProfile, Card


def payment_page(request):
    if request.user.is_authenticated:
        billing_profile = request.user.billingprofile
        stripe_id = billing_profile.stripe_id
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next', None)
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    context = {"stripe_publish_key": settings.STRIPE_PUB_KEY,
               "next": next_url}
    return render(request, 'billing/payment.html', context)


def payment_create_page(request):
    if request.method == "POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find this user"}, 401)
        token = request.POST.get('token')
        if token is not None:
            customer = stripe.Customer.retrieve(billing_profile.stripe_id)
            card_response = customer.sources.create(source=token)
            card_obj = Card.objects.add_new(billing_profile, card_response)
            print(card_obj)
        return JsonResponse({"message": "Your card was successfully added"})
    return HttpResponse("error", 401)
