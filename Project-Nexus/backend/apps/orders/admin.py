from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'unit_price', 'total_price']
    fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']
    can_delete = False

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'created_at', 'created_by']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'customer_email', 'status', 'payment_status',
        'total_amount', 'item_count', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__email', 'customer_email', 'shipping_first_name', 'shipping_last_name']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 'paid_at', 
        'shipped_at', 'delivered_at', 'cancelled_at', 'item_count',
        'full_shipping_address', 'full_billing_address'
    ]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status',
                'customer_email', 'customer_phone'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal', 'tax_amount', 'shipping_cost', 
                'discount_amount', 'total_amount'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name',
                'shipping_address_line1', 'shipping_address_line2',
                'shipping_city', 'shipping_state', 'shipping_country', 'shipping_zip_code',
                'full_shipping_address'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_first_name', 'billing_last_name',
                'billing_address_line1', 'billing_address_line2',
                'billing_city', 'billing_state', 'billing_country', 'billing_zip_code',
                'full_billing_address'
            )
        }),
        ('Payment Information', {
            'fields': (
                'payment_method', 'transaction_id', 'paid_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'shipped_at', 
                'delivered_at', 'cancelled_at'
            )
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
    )

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['product_name', 'product_sku', 'total_price', 'created_at']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'created_at', 'created_by']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__order_number']
    readonly_fields = ['created_at']