from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory

@receiver(pre_save, sender=Order)
def update_order_timestamps(sender, instance, **kwargs):
    """Update timestamps when order status changes"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Update paid_at when payment status changes to paid
            if old_instance.payment_status != 'paid' and instance.payment_status == 'paid':
                instance.paid_at = timezone.now()
            
            # Update shipped_at when status changes to shipped
            if old_instance.status != 'shipped' and instance.status == 'shipped':
                instance.shipped_at = timezone.now()
            
            # Update delivered_at when status changes to delivered
            if old_instance.status != 'delivered' and instance.status == 'delivered':
                instance.delivered_at = timezone.now()
            
            # Update cancelled_at when status changes to cancelled
            if old_instance.status != 'cancelled' and instance.status == 'cancelled':
                instance.cancelled_at = timezone.now()
                
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def create_status_history(sender, instance, created, **kwargs):
    """Create status history record when order status changes"""
    if created:
        # For new orders, record the initial status
        OrderStatusHistory.objects.create(
            order=instance,
            new_status=instance.status,
            notes="Order created"
        )
    else:
        # For existing orders, check if status changed
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                OrderStatusHistory.objects.create(
                    order=instance,
                    old_status=old_instance.status,
                    new_status=instance.status,
                    notes=f"Status changed from {old_instance.status} to {instance.status}"
                )
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=OrderItem)
@receiver(post_save, sender=Order)
def update_inventory_on_status_change(sender, instance, **kwargs):
    """Update product inventory when order status changes"""
    if isinstance(instance, Order):
        order = instance
        if order.status in ['confirmed', 'processing']:
            # Reduce inventory when order is confirmed
            for item in order.items.all():
                if item.product.track_quantity:
                    item.product.quantity = max(0, item.product.quantity - item.quantity)
                    item.product.save()
        
        elif order.status in ['cancelled', 'refunded']:
            # Restore inventory when order is cancelled or refunded
            for item in order.items.all():
                if item.product.track_quantity:
                    item.product.quantity += item.quantity
                    item.product.save()