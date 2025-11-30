from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product

class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='product_reviews'
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Status and moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Engagement metrics
    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at', '-helpful_count']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"

    def save(self, *args, **kwargs):
        # Auto-approve if rating is provided (you can modify this logic)
        if self.rating and not self.is_approved and self.status == 'pending':
            self.is_approved = True
            self.status = 'approved'
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def is_verified_purchase(self):
        """Check if the user actually purchased the product"""
        return self.user.orders.filter(
            items__product=self.product,
            status__in=['delivered', 'shipped']
        ).exists()

class ReviewImage(models.Model):
    review = models.ForeignKey(
        ProductReview, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='reviews/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Image for review {self.review.id}"

class ReviewHelpful(models.Model):
    """Track which users found which reviews helpful"""
    review = models.ForeignKey(
        ProductReview, 
        on_delete=models.CASCADE, 
        related_name='helpful_votes'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='helpful_votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']

    def __str__(self):
        return f"{self.user.email} found review {self.review.id} helpful"

class ReviewReport(models.Model):
    """Track reported reviews for moderation"""
    REPORT_REASONS = [
        ('spam', 'Spam or misleading'),
        ('inappropriate', 'Inappropriate content'),
        ('false_info', 'False information'),
        ('harassment', 'Harassment or hate speech'),
        ('other', 'Other'),
    ]

    review = models.ForeignKey(
        ProductReview, 
        on_delete=models.CASCADE, 
        related_name='reports'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='review_reports'
    )
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['review', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on review {self.review.id} by {self.user.email}"
# Create your models here.
