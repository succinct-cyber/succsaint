from django.shortcuts import render
from store.models import Product, ReviewRating
from django.contrib.auth.decorators import login_required


 
def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    for product in products:
    # Get the reviews
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    
    context = {
        'products': products,
        'reviews': reviews
    }
    return render(request, 'home.html', context)


from django.db import connection

# Disable FK checks so we can clean the log
with connection.cursor() as cursor:
    cursor.execute('PRAGMA foreign_keys = OFF;')

# Delete orphaned admin log entries
with connection.cursor() as cursor:
    cursor.execute(
        "DELETE FROM django_admin_log WHERE user_id NOT IN "
        "(SELECT id FROM accounts_account)"
    )
    print(f"Deleted {cursor.rowcount} orphaned log entries")

with connection.cursor() as cursor:
    cursor.execute('PRAGMA foreign_keys = ON;')
    