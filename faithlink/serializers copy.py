from rest_framework import serializers
from django.utils.timezone import now
from .models import (
    Parishioner,
    Donation,
    Event,
    FundraisingCampaign,
    PrayerRequest,
    SacramentRecord,
    Attendance
)
from accounts.models import CustomUser


# -------------------------
# CustomUser Serializer
# -------------------------
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


# -------------------------
# Parishioner Serializer
# -------------------------
from rest_framework import serializers
from .models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =  '__all__'

class ParishionerSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = Parishioner
        fields = '__all__'


from rest_framework import serializers
from .models import Group




# -------------------------
# Event Serializer
# -------------------------
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def validate_date(self, value):
        if value < now():
            raise serializers.ValidationError("The event date must be in the future.")
        return value


# -------------------------
# Donation Serializer
# -------------------------
class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parishioner
        fields = ['id', 'first_name', 'last_name']

class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Donation
        fields = '__all__'
        extra_kwargs = {
            'donor': {'read_only': True},  # <--- This ensures donor isn't required in POST
            'received': {'read_only': True},
        }

    def get_donor_name(self, obj):
        if obj.anonymous:
            return "Anonymous"
        return f"{obj.donor.user.first_name} {obj.donor.user.last_name}"






# class DonationSerializer(serializers.ModelSerializer):
#     donor_name = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Donation
#         fields = [
#             'id', 'donor', 'donor_name', 'type',
#             'amount', 'payment_method',
#             'item_name', 'quantity', 'item_condition', 'photo',
#             'description', 'date', 'received', 'anonymous',
#             'pickup_requested', 'approved',
#         ]
#         extra_kwargs = {
#             'donor': {'read_only': True},
#             'received': {'read_only': True},
#             'approved': {'read_only': True},
#         }

#     def get_donor_name(self, obj):
#         if obj.anonymous:
#             return "Anonymous"
#         return f"{obj.donor.user.first_name} {obj.donor.user.last_name}"

#     def validate(self, data):
#         donation_type = data.get('type')

#         if donation_type == 'money':
#             if not data.get('amount'):
#                 raise serializers.ValidationError("Amount is required for monetary donations.")
#         elif donation_type == 'item':
#             if not data.get('item_name'):
#                 raise serializers.ValidationError("Item name is required for item donations.")
#         else:
#             raise serializers.ValidationError("Invalid donation type.")

#         return data


# -------------------------
# Fundraising Campaign Serializer
# -------------------------
class FundraisingCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundraisingCampaign
        fields = '__all__'


# -------------------------
# Prayer Request Serializer
# -------------------------
class PrayerRequestSerializer(serializers.ModelSerializer):
    parishioner = serializers.StringRelatedField()

    class Meta:
        model = PrayerRequest
        fields = '__all__'


# -------------------------
# Sacrament Record Serializer
# -------------------------
from rest_framework import serializers
from .models import SacramentRecord

class SacramentRecordSerializer(serializers.ModelSerializer):
    parishioner_name = serializers.CharField(source='parishioner.name', read_only=True)

    class Meta:
        model = SacramentRecord
        fields = '__all__'


# -------------------------
# Attendance Serializer
# -------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
