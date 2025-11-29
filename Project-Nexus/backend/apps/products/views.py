from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import Category, Brand, Product, ProductReview
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductReviewSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


class BrandDetailView(generics.RetrieveAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = Product.objects.filter(status='published')
        
        # Filter by category slug
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(
                Q(category__slug=category_slug) | 
                Q(category__parent__slug=category_slug)
            )
        
        # Filter by brand slug
        brand_slug = self.request.query_params.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search) |
                Q(category__name__icontains=search) |
                Q(brand__name__icontains=search)
            )
        
        return queryset.select_related('category', 'brand').prefetch_related('images')


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(status='published').select_related(
            'category', 'brand'
        ).prefetch_related('images')


class FeaturedProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            status='published', 
            is_featured=True
        ).select_related('category', 'brand').prefetch_related('images')[:12]


class ProductReviewListView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_slug = self.kwargs.get('slug')
        return ProductReview.objects.filter(
            product__slug=product_slug,
            is_approved=True
        ).select_related('user', 'product')

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        serializer.save(user=self.request.user, product=product)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_stats(request, slug):
    try:
        product = Product.objects.get(slug=slug, status='published')
        
        # Get rating distribution
        rating_distribution = product.reviews.filter(is_approved=True).values(
            'rating'
        ).annotate(count=Count('id')).order_by('rating')
        
        stats = {
            'average_rating': product.average_rating,
            'review_count': product.review_count,
            'rating_distribution': list(rating_distribution),
            'in_stock': product.in_stock,
            'is_low_stock': product.is_low_stock,
        }
        
        return Response(stats)
        
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )