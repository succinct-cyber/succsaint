from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'is_available', 'created_date', 'modified_date', 'slug')
    list_editable = ('price', 'stock', 'is_available')
    list_filter = ('is_available', 'created_date')
    search_fields = ('product_name', 'description')

admin.site.register(Product, ProductAdmin)

# Register your models here.
