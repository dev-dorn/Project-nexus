from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at', 'updated_at']
    fields = ['product', 'quantity', 'unit_price', 'total_price', 'added_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'total_items']
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'unit_price', 'total_price', 'added_at']
    list_filter = ['added_at', 'cart__user']
    search_fields = ['cart__user__email', 'product__name']
    readonly_fields = ['added_at', 'updated_at', 'unit_price', 'total_price']