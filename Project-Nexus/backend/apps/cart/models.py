from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import User
from apps.products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_price(self):
        # In a real scenario, you might add tax, shipping, etc.
        return self.subtotal

    def clear(self):
        """Clear all items from the cart"""
        self.items.all().delete()

    def merge_with_user_cart(self, user):
        """Merge anonymous cart with user cart after login"""
        if self.user:
            return  # Already a user cart
        
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Move items from anonymous cart to user cart
        for item in self.items.all():
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        
        # Delete the anonymous cart
        self.delete()
        
        return user_cart


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['added_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.price

    @property
    def unit_price(self):
        return self.product.price

    def save(self, *args, **kwargs):
        # Check product availability
        if self.product.track_quantity and self.quantity > self.product.quantity:
            raise ValueError(f"Only {self.product.quantity} items available in stock")
        
        super().save(*args, **kwargs)