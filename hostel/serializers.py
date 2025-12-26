from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import (
    Address, 
    Hostel, 
    Student, 
    RoomAssignment,
    Room
)

# Serializers concerning the Hostel System
class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    prices = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'capacity', 'block', 'is_available', 'prices']

        extra_kwargs = {
            'room_number': {'validators': []}
        }

    def get_is_available(self, obj):
        count = getattr(obj, 'student_count', None)

        if count is None:
            count = obj.room_assignment.count()
        return count < obj.capacity

    def get_prices(self, obj):
        price_map = self.context.get('price_map')

        if price_map:
            return price_map.get(obj.capacity)

    def save(self, **kwargs):

        hostel_id = self.context['hostel_id']

        if not Hostel.objects.filter(pk=hostel_id).exists():
            raise serializers.ValidationError(
                {"hostel_id": f"Hostel with ID {hostel_id} does not exist."}
            )

        if self.instance is not None:

            self.instance.capacity = self.validated_data.get('capacity', self.instance.capacity)
            self.instance.room_number = self.validated_data.get('room_number', self.instance.room_number)
            self.instance.block = self.validated_data.get('block', self.instance.block)
            
            self.instance.save(update_fields=self.validated_data.keys())
            return self.instance
        
        else:
            with transaction.atomic():
                try:
                    hostel = Hostel.objects.select_for_update().get(id=hostel_id)
                except Hostel.DoesNotExist:
                    return serializers.ValidationError({'error': f"Hostel {hostel_id} does not exist"})
                
                if hostel.rooms.count() >= hostel.number_of_rooms:
                    raise serializers.ValidationError({'error': f"Room limit reached! Max allowed: {hostel.number_of_rooms}"})
                
                self.instance = Room.objects.create(hostel_id=hostel_id, **self.validated_data)
                return self.instance
        
class RoomAssignmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.select_related('user').all()
    )
    class Meta:
        model = RoomAssignment
        fields = ['student']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code']

class HostelSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'contact_email', 'number_of_rooms', 'address']

    def save(self, **kwargs):

        address_data = self.validated_data.pop('address', None)
        
        if self.instance is not None:

            if self.validated_data:

                for attr, value in self.validated_data.items():
                    setattr(self.instance, attr, value)

                self.instance.save(update_fields=self.validated_data.keys())

            if address_data:
                address_instance = self.instance.address

                for attr, value in address_data.items():
                    setattr(address_instance, attr, value)

                address_instance.save(update_fields=address_data.keys())
            return self.instance
        
        else:
            if not address_data:
                raise serializers.ValidationError({'address': 'Address data is required'})
            
            address = Address.objects.create(**address_data)
            self.instance = Hostel.objects.create(address=address, **self.validated_data)

            return self.instance

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

        extra_kwargs = {
            'password': {'write_only': True}
        }

class UpdateStudentSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializer()
    class Meta:
        model = Student
        fields = ['user', 'contact_info']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        try:
        
            if validated_data:
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)

                instance.save(update_fields=validated_data.keys())
            
            if user_data:
                user = instance.user
                for attr, value in user_data.items():
                    setattr(user, attr, value)

                user.save(update_fields=user_data.keys())

            return instance
        
        except IntegrityError:
            raise serializers.ValidationError({'error': 'Account with this email already exists'})

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Student
        fields = ['id', 'user', 'course', 'contact_info']

    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop('user')
            user = get_user_model().objects.create_user(**user_data)
            student = Student.objects.create(**validated_data, user=user)
        return student
    
class StudentProfileSerializer(serializers.ModelSerializer):
    room = serializers.CharField(read_only=True)
    class Meta:
        model = Student
        fields = ['course', 'contact_info', 'room']

class CustomUserSerializer(BaseUserSerializer):
    student_profile = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = get_user_model()
        fields = BaseUserSerializer.Meta.fields + ('student_profile',)

    def get_student_profile(self, obj):
        if hasattr(obj, 'student'):
            return StudentSerializer(obj.student).data








