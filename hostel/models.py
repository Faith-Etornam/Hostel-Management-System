from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

# Create your models here.

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

class Hostel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='address')
    number_of_rooms = models.IntegerField()

    def __str__(self):
        return self.name
    
class RoomPricing(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='prices')
    capacity = models.IntegerField(help_text="e.g. 1 for '1 in a room', 2 for '2 in a room'")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [['hostel', 'capacity']]

    def __str__(self):
        return f"{self.capacity} in a room - {self.price}"

class Room(models.Model):
    room_number = models.CharField(max_length=10)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    block = models.CharField(max_length=50, null=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        unique_together = [['hostel', 'room_number']]

    @property
    def is_available(self):
        if hasattr(self, 'student_count'):
            return self.student_count < self.capacity
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

class Payment(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETED = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETED, 'Completed'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=1, choices=PAYMENT_STATUS, default=PAYMENT_STATUS_PENDING)

class Student(models.Model):
    course = models.CharField(max_length=50)
    contact_info = models.CharField(max_length=10)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='students')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"