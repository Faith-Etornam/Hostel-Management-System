from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

class Hostel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    is_available = models.BooleanField(default=True)
    block = models.CharField(max_length=50)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)

