from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers

class CustomTokenSerializer(TokenCreateSerializer):
    email = serializers.EmailField()
    class Meta:
        fields = ['email', 'password']