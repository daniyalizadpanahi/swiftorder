from django.urls import path
from .views import RegisterAPI, UserProfile, SendPasswordResetEmailView, ResetPasswordView

app_name = "account"

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('profile/', UserProfile.as_view(), name='user-profile'),
    path('password-reset/', SendPasswordResetEmailView.as_view(), name='password_reset_email'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
]
