from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

CustomUser = get_user_model()


class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "profile_picture",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data.get("username", validated_data["email"]),
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            address=validated_data.get("address"),
            profile_picture=validated_data.get("profile_picture"),
            password=validated_data["password"],
        )
        return user


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "profile_picture",
            "role",
        ]
        read_only_fields = ["id", "email", "role"]
