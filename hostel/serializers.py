from rest_framework import serializers
from .models import Hostel, Address, Student, Room
from django.contrib.auth import get_user_model

# Serializers concerning the Hostel System
class RoomSerializer(serializers.ModelSerializer):
    hostel = serializers.CharField(max_length=255, read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'capacity', 'block', 'hostel']

        extra_kwargs = {
            'room_number': {'validators': []}
        }

    def save(self, **kwargs):
        hostel_id = self.context['hostel_id']

        if self.instance is not None:

            self.instance.capacity = self.validated_data.get('capacity')
            self.instance.room_number = self.validated_data.get('room_number')
            self.instance.block = self.validated_data.get('block')

            self.instance.save()
            return self.instance
        
        else:
            self.instance = Room.objects.create(hostel_id=hostel_id, **self.validated_data)
            return self.instance

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code']

class HostelSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    rooms = RoomSerializer(many=True, read_only=True)
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
        return Student.objects.create(**validated_data, user=user)








