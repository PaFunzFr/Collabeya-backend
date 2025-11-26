from rest_framework import serializers
from django.contrib.auth import authenticate
from app_auth.models import UserProfile
from django.contrib.auth.models import User
from app_auth.models import UserProfile, USER_TYPES

MAX_FILE_SIZE = 2 * 1024 * 1024

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(
        write_only=True,
        help_text="Repeat the password for confirmation."
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'write_only': True},
        }


    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    

    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        UserProfile.objects.create(user=user)

        return user