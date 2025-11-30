from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, ShippingMethod

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'estimated_days_min', 'estimated_days_max', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['price', 'is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'is_active')
        }),
        ('Delivery Estimates', {
            'fields': ('estimated_days_min', 'estimated_days_max')
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total_amount', 'shipping_method', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at', 'shipping_method']
    search_fields = ['order_number', 'user__email', 'customer_email', 'shipping_first_name', 'shipping_last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_select_related = ['user', 'shipping_method']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'shipping_method')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_address_line1', 
                      'shipping_address_line2', 'shipping_city', 'shipping_state', 
                      'shipping_country', 'shipping_zip_code')
        }),
        ('Billing Address', {
            'fields': ('billing_first_name', 'billing_last_name', 'billing_address_line1',
                      'billing_address_line2', 'billing_city', 'billing_state',
                      'billing_country', 'billing_zip_code')
        }),
        ('Payment & Notes', {
            'fields': ('payment_method', 'transaction_id', 'customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'shipped_at', 'delivered_at', 'cancelled_at', 'created_at', 'updated_at')
        })
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['order__status', 'created_at']
    search_fields = ['product_name', 'product_sku', 'order__order_number']
    readonly_fields = ['created_at']
    list_select_related = ['order']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'created_at', 'created_by']
    list_filter = ['new_status', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['order__order_number', 'notes']
    list_select_related = ['order', 'created_by']