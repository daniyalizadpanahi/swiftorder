from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from products.models import Product
from uuid import uuid4

User = get_user_model()


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETE = "C"
    PAYMENT_STATUS_FAILED = "F"
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETE, "Completed"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    )

    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING,
        verbose_name="Payment Status",
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Buyer")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Order Created At")
    total_price = models.IntegerField(verbose_name="Total Price")
    token = models.CharField(max_length=255, verbose_name="Token")
    tracking_code = models.CharField(
        max_length=16, unique=True, verbose_name="Tracking Code"
    )

    def __str__(self):
        user_orders = Order.objects.prefetch_related().filter(user=self.user).count()
        return f"{self.user} ({user_orders} orders)"

    class Meta:
        verbose_name = "Order List"
        verbose_name_plural = "Order Lists"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, verbose_name="Order", related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="orderitems",
        verbose_name="Product",
    )
    order_item_price = models.PositiveIntegerField(verbose_name="Price")
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name="Quantity")


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, verbose_name="ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cart Created At")
    last_update = models.DateTimeField(
        auto_now_add=True, verbose_name="Last Updated At"
    )

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Cart"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Product"
    )
    quantity = models.PositiveSmallIntegerField(verbose_name="Quantity")

    class Meta:
        unique_together = [["cart", "product"]]
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
