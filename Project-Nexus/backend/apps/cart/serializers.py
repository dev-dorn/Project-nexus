from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 
            'unit_price', 'total_price', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.published().get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        cart = validated_data.pop('cart')
        quantity = validated_data.get('quantity', 1)

        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        
        if existing_item:
            # Update quantity if item exists
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item
        else:
            # Create new cart item
            return CartItem.objects.create(
                cart=cart,
                product_id=product_id,
                quantity=quantity
            )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'items', 
            'total_items', 'subtotal', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'session_key', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.published().get(pk=value)
            if product.track_quantity and product.quantity < 1:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")
        return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        
        # Check product stock if tracking quantity
        if self.instance.product.track_quantity and value > self.instance.product.quantity:
            raise serializers.ValidationError(
                f"Only {self.instance.product.quantity} items available in stock"
            )
        return value