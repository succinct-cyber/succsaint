from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'variations', 'quantity', 'product_price', 'ordered')
    can_delete = False
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'state', 'city', 'order_note', 'order_total', 'tax', 'status', 'ip', 'is_ordered', 'created_at', 'updated_at')
    list_filter = ('status', 'is_ordered',)
    search_fields = ('order_number', 'full_name', 'phone', 'email')
    list_per_page = 20
    inlines = [OrderProductInline]
    

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)


# Register your models here.
