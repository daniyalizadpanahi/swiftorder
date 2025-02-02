import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from account.models import CustomUser
from products.models import Product, Category, ProductCategory
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="testuser@example.com",
        username="testuser@example.com",
        password="password123",
        role="admin",
    )


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
def api_client():
    return APIClient()


@pytest.fixture
def token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_product_list(api_client, token, product):
    url = reverse("products:all-products-list")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get(url)

    assert response.status_code == 200
    assert "name" in response.data["results"][0]
    assert response.data["results"][0]["name"] == product.name


@pytest.mark.django_db
def test_category_list(api_client, token, category):
    url = reverse("products:category-list")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get(url)
    assert response.status_code == 200
    assert "name" in response.data["results"][0]
    assert response.data["results"][0]["name"] == category.name


@pytest.mark.django_db
def test_products_by_category(api_client, product_category, product, token):
    category_id = product_category[0].category.id
    assert Category.objects.filter(id=category_id).exists(), f"Category with id {category_id} does not exist"

    url = reverse("products:products_by_category", args=[category_id])
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.get(url)

    assert response.status_code == 200
    assert "name" in response.data["results"][0]
    assert response.data["results"][0]["name"] == product.name


@pytest.mark.django_db
def test_product_create_as_admin(api_client, user, token, category):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("products:product-detail-list")
    data = {
        "name": "Laptop",
        "price": 1500,
        "stock": 5,
        "created_by": user.id,
        "categories": [category.id],
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Laptop"


@pytest.mark.django_db
def test_product_create_permission_denied(api_client, user, token):
    user.role = "user"
    user.save()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("products:product-detail-list")
    data = {
        "name": "Laptop",
        "price": 1500,
        "stock": 5,
        "categories": [],
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 403
