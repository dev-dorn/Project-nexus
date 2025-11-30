from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderItem

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

@receiver(post_save, sender=OrderItem)
def update_inventory_on_order(sender, instance, created, **kwargs):
    """Update product inventory when order items are added"""
    if created and instance.order.status in ['confirmed', 'processing']:
        if instance.product.track_quantity:
            instance.product.quantity = max(0, instance.product.quantity - instance.quantity)
            instance.product.save()