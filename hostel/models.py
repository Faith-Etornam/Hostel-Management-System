from django.db import models

# Create your models here.

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

class Hostel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT)