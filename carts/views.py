from django.shortcuts import render, redirect

from .models import Cart
from products.models import Product
from orders.models import Order


def cart_page(request):
    cart_obj, cart_new = Cart.objects.new_or_get(request=request)
    return render(request, 'carts/cart.html', {'cart': cart_obj})


def cart_update(request):
    product_id = request.POST.get("product_id", None)
    print("remove")
    if product_id:
        product_obj = Product.objects.get(id=product_id)
        if not product_obj:
            print("Product does not exist")
            return Product.DoesNotExist
        cart_obj, cart_new  = Cart.objects.new_or_get(request=request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        else:
            cart_obj.products.add(product_obj)
    request.session['cart_items'] = cart_obj.products.count()
    return redirect('carts:cart')


def checkout_page(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request=request)
    order_obj= None
    if cart_created or cart_obj.products.count() == 0:
        return redirect('carts:cart')
    else:
        order_obj, new_order_obj = Order.objects.get_or_create(cart=cart_obj)
        print("print")
        print(order_obj.total)
    return render(request, 'carts/checkout.html', {'order': order_obj})
