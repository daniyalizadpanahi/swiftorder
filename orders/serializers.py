from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from products.models import Product


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "description"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="items.all", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total_price",
            "payment_status",
            "payment_id",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class CartItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer()

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="items.all", read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items"]
        read_only_fields = ["user", "created_at"]
