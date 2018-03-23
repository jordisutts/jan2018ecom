from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .forms import OrderForm, MakePaymentForm
from products.models import Product
from decimal import Decimal
from cart.utils import get_cart_items_and_total
from django.utils import timezone
from .models import OrderLineItem
import stripe
from django.contrib import messages
from cart.utils import get_cart_items_and_total

stripe.api_key = settings.STRIPE_SECRET

# Create your views here.
def checkout(request):
    if request.method=="POST":
        #save the order
        order_form = OrderForm(request.POST)
        order = order_form.save(commit=False)
        order.date = timezone.now()
        order.save()
        
        #save order line items
        
        cart = request.session.get('cart', {})
        for id, quantity in cart.items():
            product = get_object_or_404 (Product, pk=id)
            order_line_item = OrderLineItem(
                order = order,
                product = product,
                quantity = quantity
                )
            order_line_item.save()
        
        #charge the card
        payment_form = MakePaymentForm(request.POST)
        if payment_form.is_valid():
            total = get_cart_items_and_total(cart)['total']
            total_in_cent = int(total*100)
            
            try:
               customer = stripe.Charge.create(
                   amount= total_in_cent,
                   currency="EUR",
                   description="Dummy Transaction",
                   card=payment_form.cleaned_data['stripe_id'],
               )
            except stripe.error.CardError:
               messages.error(request, "Your card was declined!")

            if customer.paid:
               messages.error(request, "You have successfully paid")
        
        #clear the cart
        del request.session['cart']
        return redirect('home')
        
    else:
        order_form = OrderForm()
        payment_form = MakePaymentForm()
        context = {'order_form': order_form, 'payment_form': payment_form, 'publishable': settings.STRIPE_PUBLISHABLE }
        cart = request.session.get('cart', {})
        cart_items_and_total = get_cart_items_and_total(cart)
        context.update(cart_items_and_total)
    
    return render(request, "checkout/checkout.html",  context)
    
