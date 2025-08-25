from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_parishioner = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
