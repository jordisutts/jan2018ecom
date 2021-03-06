from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from reviews.forms import ReviewForm

# Create your views here.
def all_products(request):
    products = Product.objects.all()
    return render(request, "products/product-list.html", {'products': products})    
    
def product_item(request, id):
    product = get_object_or_404(Product, pk=id)
    print(product)
    form = ReviewForm()
    return render(request, "products/product-item.html", {'product': product, 'review_form': form })

def search_products(request):
    match = request.GET.get('match')
    
    if match=='contains':
        products = Product.objects.filter(name__contains=request.GET['search'])
    else:
        products = Product.objects.filter(name__startswith=request.GET['search'])
        
    return render(request, "products/product-list.html", {'products': products})
    