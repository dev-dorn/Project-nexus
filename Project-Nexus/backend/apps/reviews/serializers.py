from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import ProductReview, ReviewImage, ReviewHelpful, ReviewReport
from apps.products.serializers import ProductListSerializer

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'alt_text', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductListSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    is_verified_purchase = serializers.ReadOnlyField()
    user_has_voted_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'rating', 'title', 'comment',
            'status', 'is_approved', 'is_featured', 'is_verified_purchase',
            'helpful_count', 'reported_count', 'images',
            'user_has_voted_helpful', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'product', 'status', 'is_approved', 'is_featured',
            'helpful_count', 'reported_count', 'created_at', 'updated_at'
        ]

    def get_user_has_voted_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(user=request.user).exists()
        return False

class ProductReviewCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    images = ReviewImageSerializer(many=True, required=False)
    
    class Meta:
        model = ProductReview
        fields = [
            'product_id', 'rating', 'title', 'comment', 'images'
        ]

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.published().get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")
        return value

    def validate(self, attrs):
        # Check if user already reviewed this product
        request = self.context.get('request')
        product_id = attrs.get('product_id')
        
        if request and request.user.is_authenticated:
            existing_review = ProductReview.objects.filter(
                user=request.user,
                product_id=product_id
            ).exists()
            
            if existing_review:
                raise serializers.ValidationError("You have already reviewed this product")
        
        return attrs

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product_id = validated_data.pop('product_id')
        
        review = ProductReview.objects.create(
            product_id=product_id,
            user=self.context['request'].user,
            **validated_data
        )
        
        # Create review images
        for image_data in images_data:
            ReviewImage.objects.create(review=review, **image_data)
        
        return review

class ProductReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'comment']

class ReviewHelpfulSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewHelpful
        fields = ['id', 'review', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = ['id', 'review', 'reason', 'description', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ProductReviewStatsSerializer(serializers.Serializer):
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    verified_purchases = serializers.IntegerField()
    featured_reviews = serializers.IntegerField()