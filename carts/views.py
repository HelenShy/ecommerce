from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from .models import Cart
from products.models import Product
from orders.models import Order
from billing.models import BillingProfile
from accounts.forms import LoginForm, GuestForm


def cart_page(request):
    cart_obj, cart_new = Cart.objects.new_or_get(request=request)
    return render(request, 'carts/cart.html', {'cart': cart_obj})


def cart_update(request):
    product_id = request.POST.get("product_id", None)
    if product_id:
        product_obj = Product.objects.get(id=product_id)
        if not product_obj:
            return Product.DoesNotExist
        cart_obj, cart_new  = Cart.objects.new_or_get(request=request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            removed = True
            added = False
            messages.add_message(request, messages.INFO, 'Removed successfully.')
        else:
            cart_obj.products.add(product_obj)
            removed = False
            added = True
            messages.add_message(request, messages.INFO, 'Added successfully.')
    request.session['cart_items'] = cart_obj.products.count()
    if request.is_ajax():
        return JsonResponse({"added": added,
                            "removed": removed,
                            "cart_count": cart_obj.products.count()})
    return redirect('carts:cart')


def cart_api_update(request):
    resp = {}
    cart_obj, cart_new  = Cart.objects.new_or_get(request=request)
    products = [{'name': p.name, 'price': p.price, 'url': p.get_absolute_url()}  for p in  cart_obj.products.all()]
    resp['products'] = products
    resp['total'] = cart_obj.total
    return JsonResponse(resp)


def checkout_page(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request=request)
    order_obj= None
    if cart_created or cart_obj.products.count() == 0:
        return redirect('carts:cart')
    billing_obj, billing_created = BillingProfile.objects.new_or_get(request)
    login_form = LoginForm()
    guest_form = GuestForm()
    has_card = False
    if billing_obj:
        order_obj, order_created = Order.objects.new_or_get(
            billing_obj,
            cart_obj)
        has_card = billing_obj.has_card
    if request.method == 'POST':
        if order_obj.is_prepared():
            card_id = request.POST.get("payment-card", None)
            if card_id:
                card = billing_obj.card_set.filter(pk=card_id).first()
            print(card)
            charge_paid, charge_msg = billing_obj.charge(order_obj, card)
            if charge_paid:
                order_obj.set_status_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_obj.user:
                    billing_obj.set_cards_inactive()
                return redirect('carts:success')
            else:
                print(charge_msg)
    context = {
        'billing': billing_obj,
        'order': order_obj,
        'login_form': login_form,
        'guest_form': guest_form,
        'has_card': has_card,
    }

    return render(request, 'carts/checkout.html', context)


def checkout_success_page(request):
    return render(request, 'carts/checkout_success.html',{})
