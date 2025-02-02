from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterUserSerializer, UserProfileSerializer
from .utils import (
    send_verification_email,
    send_welcome_email,
    send_password_reset_email,
)


User = get_user_model()


class RegisterEmailAPIView(APIView):
    def post(self, request):
        try:
            user = get_object_or_404(User, pk=request.user.pk)
            send_verification_email(user, request)

            return Response(
                {"message": "Verification email sent"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPI(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        send_welcome_email(user, request)
        send_verification_email(user, request)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
    def perform_create(self, serializer):
        user = serializer.save()
        return user

class UserProfile(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView
):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SendPasswordResetEmailView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Email address of the user"
                )
            },
        ),
        responses={
            200: openapi.Response(
                "Password reset email sent!",
                examples={
                    "application/json": {"message": "Password reset email sent!"}
                },
            ),
            404: openapi.Response(
                "User with this email does not exist.",
                examples={
                    "application/json": {
                        "error": "User with this email does not exist."
                    }
                },
            ),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)

            send_password_reset_email(user, request)

            return Response(
                {"message": "Password reset email sent!"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResetPasswordView(APIView):
    @swagger_auto_schema(
        operation_description="Resets the user's password using the provided token and user ID.",
        manual_parameters=[
            openapi.Parameter(
                "uidb64",
                openapi.IN_PATH,
                description="Base64 encoded user ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "token",
                openapi.IN_PATH,
                description="Password reset token",
                type=openapi.TYPE_STRING,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password for the user"
                )
            },
        ),
        responses={
            200: openapi.Response(
                "Password reset successful!",
                examples={
                    "application/json": {"message": "Password reset successful!"}
                },
            ),
            400: openapi.Response(
                "Invalid or expired token.",
                examples={"application/json": {"error": "Invalid or expired token."}},
            ),
            404: openapi.Response(
                "Invalid user.",
                examples={"application/json": {"error": "Invalid user."}},
            ),
        },
    )
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if PasswordResetTokenGenerator().check_token(user, token):
                new_password = request.data.get("new_password")
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password reset successful!"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (User.DoesNotExist, ValueError):
            return Response(
                {"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailAPI(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.is_active = True
            user.save()
            return Response(
                {"detail": "Email successfully verified."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DeleteAccountAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_deleted = True
        user.save()
        return Response({"detail": "Account deleted."}, status=status.HTTP_200_OK)
