from django.urls import path
from .views import (
    RegisterAPI,
    UserProfile,
    SendPasswordResetEmailView,
    ResetPasswordView,
    RegisterEmailAPIView,
    VerifyEmailAPI,
    DeleteAccountAPI,
)

app_name = "account"

urlpatterns = [
    path("register/", RegisterAPI.as_view(), name="register"),
    path("email-register/", RegisterEmailAPIView.as_view(), name="email_register"),
    path("verify-email/<str:uidb64>/<str:token>/", VerifyEmailAPI.as_view(), name="verify_email"),
    path("delete-account/", DeleteAccountAPI.as_view(), name="delete_account"),
    path("profile/", UserProfile.as_view(), name="user-profile"),
    path(
        "password-reset/", SendPasswordResetEmailView.as_view(), name="password_reset"
    ),
    path(
        "password-register/<str:uidb64>/<str:token>/",
        ResetPasswordView.as_view(),
        name="password_register",
    ),
]
