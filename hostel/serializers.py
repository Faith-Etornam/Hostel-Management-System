from rest_framework import serializers
from .models import Hostel, Address, Student, Room
from django.contrib.auth import get_user_model

# Serializers concerning the Hostel System
class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'capacity', 'block', 'is_available']

        extra_kwargs = {
            'room_number': {'validators': []}
        }

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
            self.instance = Room.objects.create(hostel_id=hostel_id, **self.validated_data)
            return self.instance

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

                for attrr, value in self.validated_data.items():
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
        extra_kwargs = {'password': {'write_only': True}}

class UpdateStudentSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializer()
    class Meta:
        model = Student
        fields = ['user', 'contact_info']

    def update(self, instance, validated_data):
        user_data = self.validated_data.pop('user')
        
        if self.validated_data:
            for attr, value in self.validated_data.items():
                setattr(instance, attr, value)

            instance.save(update_fields=validated_data.keys())
        
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)

            user.save(update_fields=user_data.keys())

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








