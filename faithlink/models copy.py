from django.db import models
from django.utils.timezone import now
from accounts.models import CustomUser
import random


# ----------------------------------------
# Parishioner Model
# ----------------------------------------
from django.db import models
from django.utils.timezone import now
import random
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Parishioner(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('W', 'Widowed'),
        ('D', 'Divorced'),
        ('O', 'Other'),
    ]

    parishioner_id = models.CharField(max_length=50, null=True, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    contact = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    family_group = models.CharField(max_length=255, blank=True, null=True)
    date_approved = models.DateTimeField(default=now)
    face_image = models.ImageField(upload_to='faces/', blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)

    # ✅ New Many-to-Many field for groups
    groups = models.ManyToManyField(Group, related_name='parishioners', blank=True)

    def generate_parishioner_id(self):
        part1 = random.randint(100, 999)
        part2 = random.randint(100, 999)
        return f"{part1}-{part2}"

    def save(self, *args, **kwargs):
        if not self.parishioner_id:
            new_id = self.generate_parishioner_id()
            while Parishioner.objects.filter(parishioner_id=new_id).exists():
                new_id = self.generate_parishioner_id()
            self.parishioner_id = new_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.name


# ----------------------------------------
# Event Model
# ----------------------------------------

from django.db import models
from django.utils.timezone import now

class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(default=now)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # new description field
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)  # new image field

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.name


# ----------------------------------------
# Donation Model
# ----------------------------------------
class Donation(models.Model):
    DONATION_TYPE_CHOICES = [
        ('money', 'Money'),
        ('item', 'Item'),
    ]
    donor = models.ForeignKey(Parishioner, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=DONATION_TYPE_CHOICES, default='money')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    item_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    item_condition = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='donation_items/', blank=True, null=True)
    description = models.TextField(blank=True)
    date = models.DateField(default=now)
    received = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)
    pickup_requested = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)  # For item approval

    def __str__(self):
        return f"{self.get_type_display()} Donation by {self.donor if not self.anonymous else 'Anonymous'}"


# ----------------------------------------
# Fundraising Campaign Model
# ----------------------------------------
class FundraisingCampaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


# ----------------------------------------
# Prayer Request Model
# ----------------------------------------
class PrayerRequest(models.Model):
    parishioner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    prayer_request = models.TextField()

    def __str__(self):
        return f"Prayer Request by {self.parishioner}"


# ----------------------------------------
# Sacrament Record Model
# ----------------------------------------
from django.db import models
from django.utils.timezone import now

class SacramentRecord(models.Model):
    parishioner = models.ForeignKey(Parishioner, on_delete=models.CASCADE)
    sacrament = models.CharField(max_length=100)
    date_received = models.DateField(default=now)
    place_received = models.CharField(max_length=255)
    officiant = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    certificate_requested = models.BooleanField(default=False)  # <-- add this

    def __str__(self):
        return f"{self.sacrament} - {self.parishioner.name}"


# ----------------------------------------
# Attendance Model
# ----------------------------------------
# models.py


class Attendance(models.Model):
    MASS_TYPE_CHOICES = [
        ("Morning", "Morning"),
        ("Afternoon", "Afternoon"),
        ("Evening", "Evening"),
    ]

    parishioner = models.ForeignKey(Parishioner, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("Present", "Present")])
    mass_type = models.CharField(max_length=20, choices=MASS_TYPE_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ('parishioner', 'date', 'event')

    def __str__(self):
        return f"{self.parishioner} - {self.date} - {self.status} - {self.mass_type or 'N/A'}"
