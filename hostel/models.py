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
    block = models.CharField(max_length=50)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)

    @property
    def is_available(self):
        return self.room_assignment.count() < self.capacity

class RoomAssignment(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    student = models.OneToOneField('Student', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_assignment')

    class Meta:
        unique_together = ('room', 'student')

class Fee(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)

