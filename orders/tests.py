import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from products.models import Product, Category, ProductCategory
from orders.models import Cart, CartItem
from uuid import uuid4


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        email="testuser@example.com",
        username="testuser@example.com",
        password="password",
        role="admin",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category():
    return Category.objects.create(name="Electronics")


@pytest.fixture
def product(category, user):
    product = Product.objects.create(
        name="Smartphone", price=1000, stock=10, created_by=user
    )
    ProductCategory.objects.create(product=product, category=category)
    return product


@pytest.fixture
def product_category(product, category):
    return ProductCategory.objects.get_or_create(product=product, category=category)


@pytest.fixture
def cart(user, product):
    cart = Cart.objects.create()
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.fixture
def jwt_token(api_client, user):
    response = api_client.post(
        "/api/token/", data={"username": user.username, "password": "password"}
    )
    return response.data["access"]


@pytest.mark.django_db
def test_create_order_with_valid_cart(api_client, jwt_token, cart):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    url = reverse("orders:orders-list")
    data = {"cart_id": str(cart.id)}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "tracking_code" in response.data
    assert "total_price" in response.data
    assert "items" in response.data


@pytest.mark.django_db
def test_create_order_with_invalid_cart(api_client, jwt_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    url = reverse("orders:orders-list")
    data = {"cart_id": str(uuid4())}  # Invalid cart ID
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Cart not found"


@pytest.mark.django_db
def test_add_item_to_cart(api_client, jwt_token, product):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    cart = Cart.objects.create()
    url = reverse("orders:cart-items-list", kwargs={"cart_pk": cart.id})
    data = {"product_id": product.id, "quantity": 2}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["product_id"] == product.id
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_create_cart(api_client, jwt_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    url = reverse("orders:carts-list")
    response = api_client.post(url, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    assert Cart.objects.count() == 1


@pytest.mark.django_db
def test_cart_item_unique_together(api_client, jwt_token, product):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    cart = Cart.objects.create()
    url = reverse("orders:cart-items-list", kwargs={"cart_pk": cart.id})
    data = {"product_id": product.id, "quantity": 2}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    data["quantity"] = 3
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["quantity"] == 5


@pytest.mark.django_db
def test_add_item_to_cart_with_invalid_product(api_client, jwt_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    cart = Cart.objects.create()
    url = reverse("orders:cart-items-list", kwargs={"cart_pk": cart.id})
    data = {"product_id": 99999, "quantity": 2}  # Invalid product ID
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "product_id" in response.data
    assert response.data["product_id"][0] == "There is no product with given id"


@pytest.mark.django_db
def test_cart_is_empty_when_creating_order(api_client, jwt_token, user):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {jwt_token}")
    cart = Cart.objects.create()
    product = Product.objects.create(
        name="Test Product",
        price=50,
        description="Test Product",
        stock=5,
        created_by=user,
    )
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    url = reverse("orders:orders-list")
    data = {"cart_id": str(cart.id)}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    cart.refresh_from_db()
    assert cart.items.count() == 0
