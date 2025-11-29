from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image',
            'is_active', 'meta_title', 'meta_description', 
            'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class BrandSerializer(serializers.ModelSerializer):
    products_count = serializers.ReadOnlyField()

    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'is_active', 'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price', 'compare_price',
            'category', 'category_name', 'brand', 'brand_name', 'primary_image',
            'average_rating', 'review_count', 'discount_percentage', 'in_stock',
            'is_featured', 'is_bestseller', 'is_new', 'status', 'created_at'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    brand_details = BrandSerializer(source='brand', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_price', 'cost_price', 'sku', 'barcode',
            'quantity', 'track_quantity', 'low_stock_threshold',
            'weight', 'category', 'category_details', 'brand', 'brand_details',
            'status', 'is_featured', 'is_bestseller', 'is_new',
            'meta_title', 'meta_description', 'published_at',
            'images', 'average_rating', 'review_count',
            'discount_percentage', 'in_stock', 'is_low_stock', 'created_at'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'product_name', 'user', 'user_name', 'user_email',
            'rating', 'title', 'comment', 'is_approved', 
            'helpful_count', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_images(self, obj):
        from .models import ReviewImage
        images = ReviewImage.objects.filter(review=obj)
        return [image.image.url for image in images]