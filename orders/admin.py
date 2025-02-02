from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('order_item_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'tracking_code', 'payment_status', 'total_price', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username', 'tracking_code')
    readonly_fields = ('created_at', 'tracking_code', 'token')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'order_item_price', 'quantity')
    list_filter = ('order', 'product')
    search_fields = ('order__tracking_code', 'product__name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'last_update')
    readonly_fields = ('id', 'created_at', 'last_update')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    list_filter = ('cart', 'product')
    search_fields = ('cart__id', 'product__name')