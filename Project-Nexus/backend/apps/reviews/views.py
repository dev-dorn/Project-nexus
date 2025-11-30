from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from .models import ProductReview, ReviewImage, ReviewHelpful, ReviewReport
from .serializers import (
    ProductReviewSerializer, ProductReviewCreateSerializer,
    ProductReviewUpdateSerializer, ReviewHelpfulSerializer,
    ReviewReportSerializer, ProductReviewStatsSerializer
)

class ProductReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'status', 'is_approved', 'is_featured']
    search_fields = ['title', 'comment', 'product__name']
    ordering_fields = ['rating', 'created_at', 'updated_at', 'helpful_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = ProductReview.objects.select_related('user', 'product').prefetch_related('images')
        
        # For non-staff users, only show approved reviews
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        # For product-specific reviews
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductReviewUpdateSerializer
        return ProductReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark a review as helpful"""
        review = self.get_object()
        user = request.user
        
        # Check if user already voted
        existing_vote = ReviewHelpful.objects.filter(review=review, user=user).exists()
        
        if existing_vote:
            return Response(
                {'error': 'You have already marked this review as helpful'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create helpful vote
        ReviewHelpful.objects.create(review=review, user=user)
        review.helpful_count += 1
        review.save()
        
        return Response({'message': 'Review marked as helpful'})

    @action(detail=True, methods=['post'])
    def unmark_helpful(self, request, pk=None):
        """Remove helpful mark from a review"""
        review = self.get_object()
        user = request.user
        
        # Find and delete the helpful vote
        helpful_vote = ReviewHelpful.objects.filter(review=review, user=user).first()
        
        if helpful_vote:
            helpful_vote.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save()
            return Response({'message': 'Helpful mark removed'})
        
        return Response(
            {'error': 'You have not marked this review as helpful'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a review for moderation"""
        review = self.get_object()
        user = request.user
        
        # Check if user already reported this review
        existing_report = ReviewReport.objects.filter(review=review, user=user).exists()
        
        if existing_report:
            return Response(
                {'error': 'You have already reported this review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewReportSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review)
        
        # Update reported count
        review.reported_count += 1
        review.save()
        
        return Response({'message': 'Review reported successfully'})

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = ProductReview.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get review statistics for a product"""
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate statistics
        reviews = ProductReview.objects.filter(product_id=product_id, is_approved=True)
        
        stats = {
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
            'rating_distribution': reviews.values('rating').annotate(count=Count('id')).order_by('rating'),
            'verified_purchases': reviews.filter(is_verified_purchase=True).count(),
            'featured_reviews': reviews.filter(is_featured=True).count(),
        }
        
        serializer = ProductReviewStatsSerializer(stats)
        return Response(serializer.data)

class AdminReviewViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for review moderation"""
    permission_classes = [IsAdminUser]
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'is_approved', 'is_featured', 'rating']
    search_fields = ['title', 'comment', 'user__email', 'product__name']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending review"""
        review = self.get_object()
        review.is_approved = True
        review.status = 'approved'
        review.save()
        
        return Response({'message': 'Review approved successfully'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a review"""
        review = self.get_object()
        review.is_approved = False
        review.status = 'rejected'
        review.save()
        
        return Response({'message': 'Review rejected'})

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """Feature a review"""
        review = self.get_object()
        review.is_featured = True
        review.save()
        
        return Response({'message': 'Review featured'})

    @action(detail=True, methods=['post'])
    def unfeature(self, request, pk=None):
        """Remove featured status from a review"""
        review = self.get_object()
        review.is_featured = False
        review.save()
        
        return Response({'message': 'Review unfeatured'})

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reviews for moderation"""
        pending_reviews = ProductReview.objects.filter(status='pending')
        serializer = self.get_serializer(pending_reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def reported(self, request):
        """Get reported reviews for moderation"""
        reported_reviews = ProductReview.objects.filter(reported_count__gt=0)
        serializer = self.get_serializer(reported_reviews, many=True)
        return Response(serializer.data)