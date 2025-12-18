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
        fields = ['name', 'contact_email', 'address']

    def create(self, validated_data):
        street = validated_data['address']['street']
        city = validated_data['address']['city']
        postal_code = validated_data['address']['postal_code']

        address = Address.objects.create(street=street, city=city, postal_code=postal_code)
        address_data = validated_data.pop('address')
        hostel = Hostel.objects.create(**validated_data, address=address)
        return hostel



