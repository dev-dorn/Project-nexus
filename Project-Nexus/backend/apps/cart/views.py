from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, 
    AddToCartSerializer, UpdateCartItemSerializer
)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')

    def get_object(self):
        # Get or create cart for authenticated user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=['get', 'post', 'put', 'delete'], permission_classes=[AllowAny])
    def session_cart(self, request):
        """
        Handle cart for anonymous users using session
        """
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)

        if request.method == 'GET':
            serializer = self.get_serializer(cart)
            return Response(serializer.data)

        elif request.method == 'POST':
            # Add item to session cart
            serializer = AddToCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']

            # Add item to cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(
                CartItemSerializer(cart_item).data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'PUT':
            # Clear session cart
            cart.clear()
            return Response({'message': 'Cart cleared'})

        elif request.method == 'DELETE':
            # Delete session cart
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add item to user cart"""
        cart = self.get_object()
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product_id=product_id,
                quantity=quantity
            )

        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear all items from cart"""
        cart = self.get_object()
        cart.clear()
        return Response({'message': 'Cart cleared successfully'})

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Convert cart to order"""
        from apps.orders.models import Order, OrderItem
        
        cart = self.get_object()
        
        if cart.total_items == 0:
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create order
        order = Order.objects.create(
            user=request.user,
            customer_email=request.user.email,
            # You would typically get these from user's default addresses
            shipping_first_name=request.user.first_name,
            shipping_last_name=request.user.last_name,
            shipping_address_line1="123 Main St",  # Placeholder
            shipping_city="City",
            shipping_state="State",
            shipping_country="Country",
            shipping_zip_code="12345",
            billing_first_name=request.user.first_name,
            billing_last_name=request.user.last_name,
            billing_address_line1="123 Main St",  # Placeholder
            billing_city="City",
            billing_state="State",
            billing_country="Country",
            billing_zip_code="12345",
        )

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )

        # Calculate order totals
        order.calculate_totals()

        # Clear the cart
        cart.clear()

        return Response({
            'message': 'Order created successfully',
            'order_number': order.order_number,
            'order_id': order.id
        }, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related('product')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Item removed from cart'},
            status=status.HTTP_200_OK
        )