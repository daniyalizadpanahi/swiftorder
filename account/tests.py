import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(email, password, **kwargs):
        return User.objects.create_user(
            email=email,
            username=email,
            password=password,
            first_name=kwargs.get("first_name", "Test"),
            last_name=kwargs.get("last_name", "TestUser"),
            phone_number=kwargs.get("phone_number", ""),
            address=kwargs.get("address", ""),
            role=kwargs.get("role", "user"),
            is_active=kwargs.get("is_active", True),
            is_email_verified=kwargs.get("is_email_verified", False),
            is_phone_verified=kwargs.get("is_phone_verified", False),
            is_deleted=kwargs.get("is_deleted", False),
        )

    return make_user


# Test User Registration
@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('account:register')
    data = {
        "email": "testuser@example.com",
        "username": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "strongpassword123"
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert User.objects.filter(email="testuser@example.com").exists()

# Test User Profile Retrieval
@pytest.mark.django_db
def test_user_profile_retrieve(api_client, create_user):
    user = create_user(email="user@example.com", password="password123")
    api_client.force_authenticate(user=user)
    url = reverse('account:user-profile')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["email"] == user.email


# Test User Profile Update
@pytest.mark.django_db
def test_user_profile_update(api_client, create_user):
    user = create_user(email="user@example.com", password="password123")
    api_client.force_authenticate(user=user)
    url = reverse("account:user-profile")
    data = {
        "first_name": "Updated",
        "last_name": "User"
    }
    response = api_client.put(url, data)
    assert response.status_code == 200
    assert response.data["first_name"] == "Updated"


# Test Password Reset Request
@pytest.mark.django_db
def test_password_reset_request(api_client, create_user):
    user = create_user(email="reset@example.com", password="password123")
    url = reverse('account:password_reset')
    data = {"email": user.email}
    response = api_client.post(url, data)
    assert response.status_code == 200

# Test Account Deletion
@pytest.mark.django_db
def test_account_deletion(api_client, create_user):
    user = create_user(email="delete@example.com", password="password123")
    api_client.force_authenticate(user=user)
    url = reverse('account:delete_account')
    response = api_client.post(url)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_deleted
