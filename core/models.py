from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

# Create your models here.
class User(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    