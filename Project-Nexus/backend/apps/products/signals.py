from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, ProductImage

@receiver(pre_save, sender=Product)
def update_product_slug(sender, instance, **kwargs):
    """Auto-generate slug from product name if not provided"""
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        instance.slug = slug

@receiver(pre_save, sender=Product)
def check_low_stock_alert(sender, instance, **kwargs):
    """Check if stock is low and print alert"""
    if (instance.track_quantity and 
        instance.quantity <= instance.low_stock_threshold and 
        instance.quantity > 0):
        print(f"⚠️ Low stock alert for {instance.name}: {instance.quantity} remaining")

@receiver(pre_save, sender=Product)
def handle_published_status(sender, instance, **kwargs):
    """Handle published_at timestamp when status changes to published"""
    if instance.status == 'published' and not instance.published_at:
        from django.utils import timezone
        instance.published_at = timezone.now()
    elif instance.status != 'published':
        instance.published_at = None

@receiver(pre_save, sender=ProductImage)
def ensure_single_primary_image(sender, instance, **kwargs):
    """Ensure only one primary image per product"""
    if instance.is_primary:
        # Exclude the current instance from the update if it's being saved
        ProductImage.objects.filter(
            product=instance.product, 
            is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)