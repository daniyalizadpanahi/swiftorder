from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction
import random
import string
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CreateOrderSerializer,
    OrderSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_id = request.data.get("cart_id")

        if not Cart.objects.filter(pk=cart_id).exists():
            return Response(
                {"detail": "Cart not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart = Cart.objects.get(pk=cart_id)
        if cart.items.count() == 0:
            return Response(
                {"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        def generate_tracking_code():
            return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

        tracking_code = generate_tracking_code()
        while Order.objects.filter(tracking_code=tracking_code).exists():
            tracking_code = generate_tracking_code()

        with transaction.atomic():
            total_price = sum(
                [item.quantity * (item.product.price) for item in cart.items.all()]
            )
            order = Order.objects.create(
                user=user, total_price=total_price, tracking_code=tracking_code
            )

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    order_item_price=item.product.price or item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart.items.all()
            ]
            OrderItem.objects.bulk_create(order_items)

            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CartViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.create()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        cart_id = self.kwargs["cart_pk"]
        return CartItem.objects.filter(cart_id=cart_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["cart_id"] = self.kwargs.get("cart_pk")
        return context

    def perform_create(self, serializer):
        cart_id = self.kwargs.get("cart_pk")
        serializer.save(cart_id=cart_id)
