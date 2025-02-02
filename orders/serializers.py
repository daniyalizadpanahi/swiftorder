import random
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Product,
)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "description", "stock"]


class CartItemSerializer(serializers.ModelSerializer):
    cart_item_id = serializers.IntegerField(source="id", read_only=True)
    product = CartProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.price

    class Meta:
        model = CartItem
        fields = ["cart_item_id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        total_price = 0
        for item in cart.items.all():
            product = item.product
            price = product.price
            total_price += item.quantity * price
        return total_price

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("There is no product with given id")
        return value

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["cart_id"] = self.kwargs.get("cart_pk")
        return context

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        product_inventory = Product.objects.get(pk=product_id).stock
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity

            if product_inventory < cart_item.quantity:
                raise serializers.ValidationError(
                    "The selected quantity exceeds the available inventory."
                )
            else:
                cart_item.save()

            self.instance = cart_item

        except CartItem.DoesNotExist:
            if product_inventory < quantity:
                raise serializers.ValidationError(
                    "The selected quantity exceeds the available inventory."
                )
            else:
                self.instance = CartItem.objects.create(
                    cart_id=cart_id, **self.validated_data
                )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["quantity"]

    def update(self, instance, validated_data):
        available_quantity = instance.product.inventory
        quantity = validated_data.get("quantity", instance.quantity)

        if quantity > available_quantity:
            if available_quantity == 0:
                CartItem.objects.get(pk=instance.pk).delete()
                raise serializers.ValidationError(
                    "This product has been purchased and is not available."
                )
            instance.quantity = Product.objects.get(pk=instance.product.id).inventory
            instance.save()
            raise serializers.ValidationError(
                "Only this amount of this product is available on the site."
            )

        instance.quantity = quantity
        instance.save()
        return instance


class OrderProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "name",
            "created_at",
            "description",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source="id", read_only=True)
    product = OrderProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["item_id", "product", "order_item_price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    order_id = serializers.IntegerField(source="id")
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, order):
        return sum(
            [(item.quantity * item.order_item_price) for item in order.items.all()]
        )

    class Meta:
        model = Order
        fields = [
            "order_id",
            "payment_status",
            "user",
            "created_at",
            "items",
            "total_price",
            "tracking_code",
        ]

        read_only_fields = ("payment_status", "items", "order_id", "user")


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField(write_only=True)

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise ValidationError("Cart not found")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise ValidationError("Your cart is empty")
        return cart_id