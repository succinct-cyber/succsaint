from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key # Get the session key from the request
    if not cart: # If there is no session key, create a new one
        cart = request.session.create() # Create a new session key
    return cart # Return the session key as the cart_id

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    cart_item_exists = False

    # filter() instead of get() — handles multiple CartItems for same product
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        existing_variations = list(item.variations.all())

        # Check if this cart item has the exact same variation combo
        if existing_variations == product_variation:
            item.quantity += 1  # ✅ exact match found — just increment
            item.save()
            cart_item_exists = True  # flag it so we don't create a new one
            break

    if not cart_item_exists:
        # No matching variation combo found — create a fresh CartItem
        cart_item = CartItem.objects.create(
            product=product, cart=cart, quantity=1
        )
        if len(product_variation) > 0:
            for item in product_variation:
                cart_item.variations.add(item)  # ✅ attach variations
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    # filter() instead of get() — handles multiple CartItems for same product
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        existing_variations = list(item.variations.all())

        # Find the CartItem with the exact matching variation combo
        if existing_variations == product_variation:
            if item.quantity > 1:
                item.quantity -= 1  # ✅ decrement if more than 1
                item.save()
            else:
                item.delete()  # ✅ delete if last one
            break

    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    # filter() instead of get() — handles multiple CartItems for same product
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    for item in cart_items:
        existing_variations = list(item.variations.all())

        # Find the CartItem with the exact matching variation combo
        if existing_variations == product_variation:
            item.delete()  # ✅ only delete the matching one
            break

    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart using the cart_id from the session
        cart_items = CartItem.objects.filter(cart=cart, active=True) # Get all active cart items for the cart
        for cart_item in cart_items: # Loop through each cart item
            total += (cart_item.product.price * cart_item.quantity) # Calculate the total price by multiplying the product price by the quantity and adding it to the total
            quantity += cart_item.quantity # Add the quantity of the cart item to the total quantity
        
        tax = (2 * total) / 100 # Calculate tax as 2% of the total
        grand_total = total + tax # Calculate the grand total by adding the tax to the total
    except Cart.DoesNotExist:
        pass # If the cart does not exist, do nothing

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context) # Render the cart template with the context containing total, quantity, and cart items

# Create your views here.
