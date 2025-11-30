from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, ShippingMethod
from apps.products.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_name = serializers.ReadOnlyField()
    product_sku = serializers.ReadOnlyField()
    product_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 
            'product_price', 'quantity', 'total_price', 
            'product_data', 'created_at'
        ]
        read_only_fields = [
            'id', 'product_name', 'product_sku', 'product_price', 
            'total_price', 'product_data', 'created_at'
        ]

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'old_status', 'new_status', 'notes', 
            'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    item_count = serializers.ReadOnlyField()
    full_shipping_address = serializers.ReadOnlyField()
    full_billing_address = serializers.ReadOnlyField()
    user = serializers.StringRelatedField(read_only=True)
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'customer_email', 'customer_phone',
            'shipping_first_name', 'shipping_last_name', 'shipping_address_line1',
            'shipping_address_line2', 'shipping_city', 'shipping_state', 
            'shipping_country', 'shipping_zip_code', 'full_shipping_address',
            'billing_same_as_shipping', 'billing_first_name', 'billing_last_name',
            'billing_address_line1', 'billing_address_line2', 'billing_city',
            'billing_state', 'billing_country', 'billing_zip_code', 'full_billing_address',
            'shipping_method', 'tracking_number', 'shipping_carrier',
            'customer_notes', 'admin_notes',
            'items', 'status_history', 'item_count',
            'can_be_cancelled', 'can_be_refunded',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 
            'delivered_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'created_at', 'updated_at', 
            'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at',
            'subtotal', 'total_amount', 'item_count', 'full_shipping_address',
            'full_billing_address', 'can_be_cancelled', 'can_be_refunded'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    shipping_method_id = serializers.UUIDField(required=False)
    
    class Meta:
        model = Order
        fields = [
            'shipping_first_name', 'shipping_last_name', 'shipping_address_line1',
            'shipping_address_line2', 'shipping_city', 'shipping_state', 
            'shipping_country', 'shipping_zip_code', 'customer_phone',
            'billing_same_as_shipping', 'billing_first_name', 'billing_last_name',
            'billing_address_line1', 'billing_address_line2', 'billing_city',
            'billing_state', 'billing_country', 'billing_zip_code',
            'shipping_method_id', 'customer_notes'
        ]

    def validate(self, attrs):
        # Validate billing address if not same as shipping
        if not attrs.get('billing_same_as_shipping', True):
            billing_fields = [
                'billing_first_name', 'billing_last_name', 'billing_address_line1',
                'billing_city', 'billing_state', 'billing_country', 'billing_zip_code'
            ]
            for field in billing_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        f"{field.replace('_', ' ').title()} is required when billing address is different from shipping"
                    )
        return attrs

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'tracking_number', 'shipping_carrier',
            'admin_notes'
        ]

class OrderItemCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.published().get(pk=value)
            if product.track_quantity and product.quantity < 1:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value