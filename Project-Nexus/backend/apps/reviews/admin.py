from django.contrib import admin
from .models import ProductReview, ReviewImage, ReviewHelpful, ReviewReport

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    fields = ['image', 'alt_text']

class ReviewHelpfulInline(admin.TabularInline):
    model = ReviewHelpful
    extra = 0
    readonly_fields = ['user', 'created_at']
    can_delete = False

class ReviewReportInline(admin.TabularInline):
    model = ReviewReport
    extra = 0
    readonly_fields = ['user', 'reason', 'description', 'created_at']
    can_delete = False

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product', 'user', 'rating', 'title', 'status', 
        'is_approved', 'is_featured', 'helpful_count', 'created_at'
    ]
    list_filter = ['status', 'is_approved', 'is_featured', 'rating', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    inlines = [ReviewImageInline, ReviewHelpfulInline, ReviewReportInline]
    actions = ['approve_reviews', 'reject_reviews', 'feature_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True, status='approved')
        self.message_user(request, "Selected reviews were approved successfully")
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False, status='rejected')
        self.message_user(request, "Selected reviews were rejected")
    reject_reviews.short_description = "Reject selected reviews"

    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, "Selected reviews were featured")
    feature_reviews.short_description = "Feature selected reviews"

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'image', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name', 'review__user__email']

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__product__name', 'user__email']
    readonly_fields = ['created_at']

@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'user', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['review__product__name', 'user__email', 'description']
    readonly_fields = ['created_at']
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, "Selected reports were marked as resolved")
    mark_resolved.short_description = "Mark selected reports as resolved"