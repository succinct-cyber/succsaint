# orders/views.py\
import json
import datetime
import requests

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # ── Guard: bounce GET requests, only POST allowed ─────────────
    # The checkout form submits via POST — a direct GET to this URL
    # should just send the user back to checkout
    if request.method != 'POST':
        return redirect('checkout')

    # ── Fetch cart items for this user ────────────────────────────
    cart_items  = CartItem.objects.filter(user=current_user)
    cart_count  = cart_items.count()

    # ── Guard: empty cart → nothing to order ──────────────────────
    if cart_count <= 0:
        return redirect('store')

    # ── Calculate totals ──────────────────────────────────────────
    grand_total = 0
    tax         = 0

    for cart_item in cart_items:
        total    += (cart_item.product.price * cart_item.quantity)  # ← += not =
        quantity += cart_item.quantity

    tax         = (2 * total) / 100   # 2% VAT — adjust as needed
    grand_total = total + tax

    # ── Validate and save the order form ──────────────────────────
    form = OrderForm(request.POST)

    if form.is_valid():

        # Build the Order object — user MUST be set before .save()
        data                = Order()
        data.user           = current_user
        data.first_name     = form.cleaned_data['first_name']
        data.last_name      = form.cleaned_data['last_name']
        data.phone          = form.cleaned_data['phone']
        data.email          = form.cleaned_data['email']
        data.address_line_1 = form.cleaned_data['address_line_1']
        data.address_line_2 = form.cleaned_data['address_line_2']
        data.country        = form.cleaned_data['country']
        data.state          = form.cleaned_data['state']
        data.city           = form.cleaned_data['city']
        data.order_note     = form.cleaned_data['order_note']
        data.order_total    = grand_total
        data.tax            = tax
        data.ip             = request.META.get('REMOTE_ADDR')
        data.save()  # first save to get the auto-generated id

        # ── Generate order number: e.g. "2026031342" ──────────────
        # We use today's date + the DB-assigned id to guarantee uniqueness
        current_date      = datetime.date.today().strftime('%Y%m%d')
        data.order_number = current_date + str(data.id)
        data.save()  # second save to store the order number

        # ── Fetch the saved order to pass to payment page ─────────
        order = Order.objects.get(
            user         = current_user,
            is_ordered   = False,
            order_number = data.order_number
        )

        context = {
            'order'              : order,
            'cart_items'         : cart_items,
            'total'              : total,
            'tax'                : tax,
            'grand_total'        : grand_total,
            'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,  # for the JS popup
        }
        return render(request, 'orders/payment.html', context)

    # Form invalid — re-render checkout with errors
    return render(request, 'orders/place_order.html', {'form': form})


@login_required(login_url='login')
def payments(request):
    """
    Called via AJAX from payment.html after Paystack popup confirms.
    1. Receives the Paystack reference + order number
    2. Verifies the transaction with Paystack's API (server-side)
    3. Saves Payment, finalises Order, creates OrderProducts, clears cart
    """
    body      = json.loads(request.body)  # parse AJAX JSON payload
    order     = Order.objects.get(
                    user         = request.user,
                    is_ordered   = False,
                    order_number = body['orderID']
                )
    reference = body['transID']  # Paystack transaction reference from frontend


    # ── Server-side verification with Paystack API ────────────────
    # NEVER trust the frontend result alone — always verify from backend
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type' : 'application/json',
    }
    url      = f'https://api.paystack.co/transaction/verify/{reference}'
    response = requests.get(url, headers=headers)
    result   = response.json()

    # ── Payment confirmed by Paystack ─────────────────────────────
    if result['data']['status'] == 'success':

        # Save the payment record
        payment                = Payment()
        payment.user           = request.user
        payment.payment_id     = reference
        payment.payment_method = 'Paystack'
        payment.amount_paid    = result['data']['amount'] / 100  # kobo → naira
        payment.status         = result['data']['status']
        payment.save()

        # Mark the order as completed
        order.payment    = payment
        order.is_ordered = True
        order.save()

        # ── Create OrderProduct for each cart item ─────────────
        # This is the permanent record of what was in the order
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            order_product               = OrderProduct()
            order_product.order         = order
            order_product.payment       = payment
            order_product.user          = request.user
            order_product.product       = item.product
            order_product.quantity      = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered       = True
            order_product.save()

            # Copy ManyToMany variations (size, colour, etc.)
            order_product.variations.set(item.variations.all())
            order_product.save()

            # ── Reduce stock ───────────────────────────────────
            product         = item.product
            product.stock  -= item.quantity
            product.save()

        # ── Clear the user's cart ──────────────────────────────
        CartItem.objects.filter(user=request.user).delete()

        # send order confirmation email here (optional)
        try:
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_confirmation_email.html', {
                'user': request.user,
                'order': order,
            })
            send_email = EmailMessage(
                subject=mail_subject, 
                body=message,
                to=[request.user.email]
            )

            send_email.content_subtype = 'html'
            send_email.send()
        except Exception as e:
    
        # ── Return success to the AJAX call in payment.html ───
            return JsonResponse({
                'status'      : 'success',
                'order_number': order.order_number,
                'payment_id'  : payment.payment_id,
            })

    # ── Payment failed or was tampered with ───────────────────────
    return JsonResponse({'status': 'failed'}, status=400)


def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id   = request.GET.get('payment_id')

    try:
        order          = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order=order)
        payment        = Payment.objects.get(payment_id=payment_id)
        subtotal       = sum(
                            item.product_price * item.quantity
                            for item in order_products
                         )
        context = {
            'order'         : order,
            'order_products': order_products,
            'payment'       : payment,
            'subtotal'      : subtotal,
        }
        return render(request, 'orders/order_complete.html', context)

    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')