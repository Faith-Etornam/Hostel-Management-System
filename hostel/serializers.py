from rest_framework import serializers
from .models import Hostel, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code']

class HostelSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'contact_email', 'address']

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        return Hostel.objects.create(**validated_data, address=address)



