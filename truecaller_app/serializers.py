from rest_framework import serializers
from .models import Contact, UserContactRelation, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    # Add a field for the associated User's username
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["username", "phone_number", "spam", "email"]

    def get_username(self, obj):
        # Retrieve the associated User's username
        return obj.user.username


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["name", "phone_number", "spam", "email"]
