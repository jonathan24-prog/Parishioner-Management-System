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
from .models import Group, Parishioner, Membership, Announcement, GroupEvent

class ParishionerBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parishioner
        fields = ['id', 'name', 'first_name', 'last_name']

class MembershipSerializer(serializers.ModelSerializer):
    parishioner = ParishionerBriefSerializer(read_only=True)
    parishioner_id = serializers.PrimaryKeyRelatedField(
        queryset=Parishioner.objects.all(), write_only=True, source='parishioner'
    )

    class Meta:
        model = Membership
        fields = ['id', 'parishioner', 'parishioner_id', 'role', 'status', 'requested_at', 'approved_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = ParishionerBriefSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_by', 'created_at']

class GroupEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupEvent
        fields = ['id', 'title', 'description', 'start_at', 'end_at', 'location']

class GroupSerializer(serializers.ModelSerializer):
    leader = ParishionerBriefSerializer(read_only=True)
    leader_id = serializers.PrimaryKeyRelatedField(
        queryset=Parishioner.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
        source='leader'
    )
    members_count = serializers.IntegerField(read_only=True)
    # user-context fields
    is_member = serializers.SerializerMethodField()
    request_pending = serializers.SerializerMethodField()
    pending_requests_count = serializers.SerializerMethodField()  # NEW

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'type', 'leader', 'leader_id',
            'created_at', 'active', 'members_count', 'is_member',
            'request_pending', 'pending_requests_count'  # NEW
        ]

    def get_is_member(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            parish = Parishioner.objects.get(user=request.user)
        except Parishioner.DoesNotExist:
            return False
        return Membership.objects.filter(group=obj, parishioner=parish, status='APPROVED').exists()

    def get_request_pending(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            parish = Parishioner.objects.get(user=request.user)
        except Parishioner.DoesNotExist:
            return False
        return Membership.objects.filter(group=obj, parishioner=parish, status='PENDING').exists()

    def get_pending_requests_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        if request.user.is_staff or (obj.leader and obj.leader.user == request.user):
            return Membership.objects.filter(group=obj, status='PENDING').count()
        return 0


class ParishionerSerializer(serializers.ModelSerializer):
    # Optional: keep groups as read-only summarized list
    class Meta:
        model = Parishioner
        fields = '__all__'
        read_only_fields = ['groups']



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
            'donor': {'read_only': True},   # keep donor locked (set from backend)
            # remove "received" here so it's writable
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
