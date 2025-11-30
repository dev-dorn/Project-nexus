from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory, ShippingMethod
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    OrderItemSerializer, OrderItemCreateSerializer,
    OrderStatusHistorySerializer, ShippingMethodSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status']
    search_fields = ['order_number', 'customer_email', 'shipping_first_name', 'shipping_last_name']
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().prefetch_related('items', 'status_history')
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'status_history')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        # Create order with current user
        order = serializer.save(
            user=self.request.user,
            customer_email=self.request.user.email
        )
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            new_status=order.status,
            notes="Order created",
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to order"""
        order = self.get_object()
        
        # Check if order can be modified
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Cannot add items to order in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if item already exists in order
        existing_item = order.items.filter(product_id=serializer.validated_data['product_id']).first()
        if existing_item:
            existing_item.quantity += serializer.validated_data['quantity']
            existing_item.save()
            item_serializer = OrderItemSerializer(existing_item)
        else:
            order_item = OrderItem.objects.create(
                order=order,
                product_id=serializer.validated_data['product_id'],
                quantity=serializer.validated_data['quantity']
            )
            item_serializer = OrderItemSerializer(order_item)
        
        return Response(item_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status='pending',
            new_status='cancelled',
            notes="Order cancelled by user",
            created_by=request.user
        )
        
        return Response({'message': 'Order cancelled successfully'})

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can update order status")
        
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status=order.status,
            new_status=new_status,
            notes=notes,
            created_by=request.user
        )
        
        # Update order status
        order.status = new_status
        
        # Update timestamps based on status
        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.save()
        
        return Response({'message': f'Order status updated to {new_status}'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get order statistics"""
        if request.user.is_staff:
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(user=request.user)
        
        stats = {
            'total_orders': queryset.count(),
            'pending_orders': queryset.filter(status='pending').count(),
            'completed_orders': queryset.filter(status='delivered').count(),
            'cancelled_orders': queryset.filter(status='cancelled').count(),
            'total_revenue': sum(order.total_amount for order in queryset.filter(payment_status='paid')),
        }
        
        return Response(stats)


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all().select_related('order', 'product')
        return OrderItem.objects.filter(order__user=self.request.user).select_related('order', 'product')

    def perform_destroy(self, instance):
        # Check if order can be modified
        if instance.order.status not in ['pending', 'confirmed']:
            raise ValidationError("Cannot remove items from order in its current status")
        
        super().perform_destroy(instance)


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [IsAuthenticated]


class AdminOrderViewSet(viewsets.ModelViewSet):
    """Admin-only viewset for order management"""
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().prefetch_related('items', 'status_history')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'user']
    search_fields = ['order_number', 'customer_email', 'shipping_first_name', 'shipping_last_name']
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark order as paid"""
        order = self.get_object()
        order.payment_status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        return Response({'message': 'Order marked as paid'})

    @action(detail=True, methods=['post'])
    def mark_as_shipped(self, request, pk=None):
        """Mark order as shipped"""
        order = self.get_object()
        
        tracking_number = request.data.get('tracking_number')
        shipping_carrier = request.data.get('shipping_carrier')
        
        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.tracking_number = tracking_number
        order.shipping_carrier = shipping_carrier
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            old_status='processing',
            new_status='shipped',
            notes=f"Order shipped with {shipping_carrier}. Tracking: {tracking_number}",
            created_by=request.user
        )
        
        return Response({'message': 'Order marked as shipped'})