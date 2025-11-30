from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from apps.accounts.models import User
from apps.products.models import Product

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estimated_days_min = models.PositiveIntegerField(default=3)
    estimated_days_max = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Order Information
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Customer Information
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Shipping Address
    shipping_first_name = models.CharField(max_length=100)
    shipping_last_name = models.CharField(max_length=100)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)
    
    # Billing Address (can be same as shipping)
    billing_first_name = models.CharField(max_length=100)
    billing_last_name = models.CharField(max_length=100)
    billing_address_line1 = models.CharField(max_length=255)
    billing_address_line2 = models.CharField(max_length=255, blank=True, null=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_country = models.CharField(max_length=100)
    billing_zip_code = models.CharField(max_length=20)
    
    # Payment Information
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Notes
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    shipping_method = models.ForeignKey(
         ShippingMethod,
         on_delete=models.SET_NULL,
         null=True,
         blank=True,
         related_name='orders'
     )
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Don't calculate totals here - it will be done after order items are added
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        return f"ORD{''.join(random.choices(string.digits, k=10))}"

    def calculate_totals(self):
        """Calculate order totals from items - only call after order is saved"""
        if self.pk:  # Only calculate if order has been saved
            items_total = sum(item.total_price for item in self.items.all())
            self.subtotal = items_total - self.discount_amount
            self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
            # Save the calculated totals
            self.save(update_fields=['subtotal', 'total_amount'])

    @property
    def item_count(self):
        return self.items.count()

    @property
    def full_shipping_address(self):
        address_parts = [
            self.shipping_first_name + ' ' + self.shipping_last_name,
            self.shipping_address_line1,
            self.shipping_address_line2,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_zip_code}",
            self.shipping_country
        ]
        return ', '.join(filter(None, address_parts))

    @property
    def full_billing_address(self):
        address_parts = [
            self.billing_first_name + ' ' + self.billing_last_name,
            self.billing_address_line1,
            self.billing_address_line2,
            f"{self.billing_city}, {self.billing_state} {self.billing_zip_code}",
            self.billing_country
        ]
        return ', '.join(filter(None, address_parts))
     


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=255)  # Snapshot of product name at time of order
    product_sku = models.CharField(max_length=100)   # Snapshot of product SKU at time of order
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Product details snapshot
    product_data = models.JSONField(default=dict)  # Store product details at time of order
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def save(self, *args, **kwargs):
        # Capture product data if this is a new order item
        if not self.pk and self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_data = {
                'name': self.product.name,
                'slug': self.product.slug,
                'description': self.product.short_description or self.product.description[:200],
                'image': self.product.images.filter(is_primary=True).first().image.url if self.product.images.filter(is_primary=True).exists() else None,
                'brand': self.product.brand.name if self.product.brand else None,
                'category': self.product.category.name if self.product.category else None,
            }
        
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
        
        # Update order totals after saving the item
        if self.order:
            self.order.calculate_totals()


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order status history'

    def __str__(self):
        return f"Order #{self.order.order_number} - {self.old_status} → {self.new_status}"