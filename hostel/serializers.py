from rest_framework import serializers
from .models import Hostel, Address, Student, Room
from django.contrib.auth import get_user_model

# Serializers concerning the Hostel System
class RoomSerializer(serializers.ModelSerializer):
    hostel = serializers.CharField(max_length=255)
    class Meta:
        model = Room
        fields = ['room_number', 'capacity', 'block']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code']

class HostelSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    rooms = RoomSerializer(many=True)
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'contact_email', 'address', 'rooms']

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        return Hostel.objects.create(**validated_data, address=address)
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address')
        Address.objects.filter(pk=instance.address.pk).update(**address_data)

        Hostel.objects.filter(pk=instance.pk).update(**validated_data)
        instance.refresh_from_db()
        return instance
    

# Serializers concerning the Users and students
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name']

        extra_kwargs = {
            'email': {'validators': []}
        }
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class UpdateStudentSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializer()
    class Meta:
        model = Student
        fields = ['user', 'contact_info']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        get_user_model().objects.filter(pk=instance.user.pk).update(**user_data)
        Student.objects.filter(pk=instance.pk).update(**validated_data)
        instance.refresh_from_db()
        return instance

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Student
        fields = ['id', 'user', 'course', 'hostel', 'contact_info']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_user_model().objects.create_user(**user_data)
        student = Student.objects.create(**validated_data, user=user)
        return student
    








