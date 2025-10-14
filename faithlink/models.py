from django.db import models
from django.utils.timezone import now
from accounts.models import CustomUser
import random


# ----------------------------------------
# Parishioner Management Models
# app: faithlink
# ----------------------------------------
from django.db import models
from django.utils.timezone import now, make_aware
from datetime import datetime
from django.conf import settings
import random

from accounts.models import CustomUser  # Adjust path if needed

# =========================================================
# Utility Function
# =========================================================
def safe_parse_datetime(value):
    """
    Safely parse a value into a timezone-aware datetime.
    - Accepts datetime objects or ISO format strings.
    - Falls back to current time if parsing fails.
    """
    if isinstance(value, datetime):
        return make_aware(value) if value.tzinfo is None else value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return make_aware(dt) if dt.tzinfo is None else dt
        except ValueError:
            return now()
    return now()  # Default fallback


# =========================================================
# Group Model
# =========================================================
class Group(models.Model):
    """
    Represents a parish group or ministry (e.g., Choir, Bible Study).
    """
    TYPE_CHOICES = [
        ('Choir', 'Choir'),
        ('Youth Ministry', 'Youth Ministry'),
        ('Bible Study', 'Bible Study'),
        ('Ushering', 'Ushering'),
        ('Praise & Worship', 'Praise & Worship'),
        ('Committee', 'Committee'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Other')

    # A group can have a designated leader (Parishioner)
    leader = models.ForeignKey(
        'Parishioner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_groups'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================================================
# Parishioner Model
# =========================================================
class Parishioner(models.Model):
    """
    Represents an individual parishioner linked to a user account.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('W', 'Widowed'),
        ('D', 'Divorced'),
        ('O', 'Other')
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

    # Many-to-many relation through Membership
    groups = models.ManyToManyField('Group', through='Membership', related_name='parishioners', blank=True)

    def generate_parishioner_id(self):
        """Generate a unique parishioner ID (format: ###-###)."""
        part1 = random.randint(100, 999)
        part2 = random.randint(100, 999)
        return f"{part1}-{part2}"

    def save(self, *args, **kwargs):
        """Ensure parishioner_id is generated and unique before saving."""
        if not self.parishioner_id:
            new_id = self.generate_parishioner_id()
            while Parishioner.objects.filter(parishioner_id=new_id).exists():
                new_id = self.generate_parishioner_id()
            self.parishioner_id = new_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.name


# =========================================================
# Membership Model
# =========================================================
class Membership(models.Model):
    """
    Intermediate model linking Parishioner and Group.
    Handles role, status, and approval dates.
    """
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('LEADER', 'Leader'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    parishioner = models.ForeignKey('Parishioner', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('parishioner', 'group')

    def save(self, *args, **kwargs):
        """
        Auto-approve if role is LEADER.
        Ensure approved_at is valid and timezone-aware.
        """
        if self.role == 'LEADER' and self.status != 'APPROVED':
            self.status = 'APPROVED'
            if not self.approved_at:
                self.approved_at = now()

        if self.approved_at:
            self.approved_at = safe_parse_datetime(self.approved_at)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parishioner} -> {self.group} ({self.role}/{self.status})"


# =========================================================
# Announcement Model
# =========================================================
class Announcement(models.Model):
    """
    Announcements posted within a specific group.
    """
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey('Parishioner', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.group.name}] {self.title}"


# =========================================================
# GroupEvent Model
# =========================================================
class GroupEvent(models.Model):
    """
    Events organized by a specific group.
    """
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        """Validate and normalize datetime fields."""
        self.start_at = safe_parse_datetime(self.start_at)
        if self.end_at:
            self.end_at = safe_parse_datetime(self.end_at)
            if self.end_at < self.start_at:
                raise ValueError("End time cannot be before start time")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.group.name})"


# =========================================================
# ActivityLog Model
# =========================================================
class ActivityLog(models.Model):
    """
    Logs activities performed in a group (e.g., joins, posts).
    """
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='activity_logs')
    actor = models.ForeignKey('Parishioner', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.group.name}: {self.action}"

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

    # ✅ Changed: removed choices to allow free text
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
    approved = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )

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
# models.py
class PrayerRequest(models.Model):
    parishioner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    prayer_request = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)  # ✅ Add this field

    def __str__(self):
        return f"Prayer Request by {self.parishioner}"



# ----------------------------------------
# Sacrament Record Model
# ----------------------------------------
from django.db import models
from django.utils.timezone import now
# ----------------------------------------
# Sacrament Record Model
# ----------------------------------------
from django.db import models
from django.utils.timezone import now

class SacramentRecord(models.Model):
    parishioner = models.ForeignKey("Parishioner", on_delete=models.CASCADE)
    sacrament = models.CharField(max_length=100)
    date_received = models.DateField(default=now)
    place_received = models.CharField(max_length=255)
    officiant = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    certificate_requested = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)   # <-- NEW FIELD

    def __str__(self):
        return f"{self.sacrament} - {self.parishioner.name}"



from django.db import models
from django.utils.timezone import now

class CertificateRequest(models.Model):
    SACRAMENT_CHOICES = [
        ("Baptism", "Baptism"),
        ("Confirmation", "Confirmation"),
        ("Eucharist", "Eucharist"),
        ("Marriage", "Marriage"),
        ("Anointing of the Sick", "Anointing of the Sick"),
    ]

    parishioner = models.ForeignKey("Parishioner", on_delete=models.CASCADE)
    sacrament = models.CharField(max_length=100, choices=SACRAMENT_CHOICES)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")],
        default="Pending"
    )
    linked_record = models.ForeignKey(
        "SacramentRecord",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Optional: link this request to an actual record later"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parishioner} - {self.sacrament} ({self.status})"

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
