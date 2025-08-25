# views.py

# --- Imports ---
import json
from datetime import date
from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response





from reportlab.pdfgen import canvas
from reportlab.lib import colors
from rest_framework.views import APIView
import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
import textwrap



from accounts.models import CustomUser
from .forms import ParishionerFormUpdate
from .models import (
    Attendance,
    Donation,
    Event,
    FundraisingCampaign,
    Parishioner,
    PrayerRequest,
    SacramentRecord,
)
from .serializers import (
    AttendanceSerializer,
    CustomUserSerializer,
    DonationSerializer,
    EventSerializer,
    FundraisingCampaignSerializer,
    ParishionerSerializer,
    PrayerRequestSerializer,
    SacramentRecordSerializer,
)

from .utils import get_parishionerSignup


from django.contrib.auth.decorators import login_required
from .models import Attendance
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Event, Attendance, Parishioner


from django.shortcuts import render, get_object_or_404
from .models import Attendance, Parishioner

from django.utils import timezone
from .models import Parishioner, Event, Attendance
# --- Function-based views ---

from datetime import date, timedelta
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Q
from faithlink.models import Event, Parishioner

@login_required
def dashboard_view(request):
    context = get_parishionerSignup(request.user)

    today = date.today()
    context['today'] = today
    context['upcoming_events'] = Event.objects.filter(date__gte=now()).order_by('date')[:5]

    end_date = today + timedelta(days=7)

    birthdays = Parishioner.objects.filter(
        birthdate__isnull=False
    ).annotate(
        birth_month=ExtractMonth('birthdate'),
        birth_day=ExtractDay('birthdate')
    ).filter(
        birth_month__gte=today.month,
        birth_day__gte=today.day,
        birth_month__lte=end_date.month
    ).order_by('birth_month', 'birth_day')

    def calculate_age(birthdate, today):
        age = today.year - birthdate.year
        if (today.month, today.day) < (birthdate.month, birthdate.day):
            age -= 1
        return age + 1  # Turning this age soon

    context['birthdays'] = [
        {
            "name": f"{p.first_name} {p.last_name}" if p.first_name and p.last_name else p.name,
            "date": p.birthdate.strftime('%B %d'),
            "turning": calculate_age(p.birthdate, today)
        }
        for p in birthdays
    ]

    context['anniversaries'] = [
        {"name": "John & Maria", "date": "July 15"},
    ]

    return render(request, 'faithlink/dashboard.html', context)




def LandingPage_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/landing_page.html', context)

def parishioners_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/parishioners.html', context)

def parishionersReq_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/parishioners_request.html', context)

def events_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/events.html', context)

def events_view_user(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/events_user.html', context)

def financial_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/financial_management.html', context)

def sacramentals_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/sacramentals.html', context)

def sacramentals_view_user(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/sacramental_parishioner.html', context)

def prayer_request_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/prayer_request.html', context)

def MyQr_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/MyQR.html', context)

def privacy_policy(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/privacy_policy.html', context)

def user_donation_view(request):
    context = get_parishionerSignup(request.user)
    return render(request, 'faithlink/donation_parishioner.html', context)

def receipt_view(request, pk):
   
    donation = get_object_or_404(Donation, pk=pk)

    if not request.user.is_staff and donation.donor.user != request.user:
        return render(request, '403.html', status=403)

    return render(request, 'faithlink/receipt.html', {'donation': donation})




now = timezone.now()

def attendance_view(request):
    # context = get_parishionerSignup(request.user)
    events = Event.objects.filter(date__gte=timezone.now())
    return render(request, 'faithlink/attendance.html', {'events': events} )

def myattendance_view(request):
    # context = get_parishionerSignup(request.user)
    events = Event.objects.filter(date__gte=timezone.now())
    return render(request, 'faithlink/MyAttendance.html', {'events': events} )


def profile(request):
    parishioner = get_object_or_404(Parishioner, user=request.user)
    return render(request, 'faithlink/profile.html', {'parishioner': parishioner})

@login_required
def generate_parishioner_qr(request):
    try:
        parishioner = Parishioner.objects.get(user=request.user)
    except Parishioner.DoesNotExist:
        return HttpResponse("Parishioner not found", status=404)

    qr_data = parishioner.parishioner_id
    img = qrcode.make(qr_data)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    response = HttpResponse(buf.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename={parishioner.parishioner_id}_qr.png'
    return response

def editparishioner(request, pk):
    parishioner = get_object_or_404(Parishioner, pk=pk)
    if request.method == 'POST':
        form = ParishionerFormUpdate(request.POST, instance=parishioner)
        if form.is_valid():
            form.save()
            return redirect('parishioners')
    else:
        form = ParishionerFormUpdate(instance=parishioner)
    return render(request, 'faithlink/edit_parishioner.html', {'form': form})


def attendance_scan_view(request):
    return render(request, 'attendance.html')



def attendance_history(request):
    attendance_records = Attendance.objects.select_related('parishioner__user').order_by('-date')

    morning_mass = attendance_records.filter(mass_type="Morning", event__isnull=True)
    afternoon_mass = attendance_records.filter(mass_type="Afternoon", event__isnull=True)
    evening_mass = attendance_records.filter(mass_type="Evening", event__isnull=True)
    event_attendance = attendance_records.filter(event__isnull=False)

    all_parishioners = Parishioner.objects.select_related('user').all()
    
    unique_mass_dates = (
        Attendance.objects
        .filter(event__isnull=True)
        .values_list('date', flat=True)
        .distinct()
    )

    absentee_summary = []

    # Process mass-based attendance (check if attended ANY time on that date)
    for mass_date in unique_mass_dates:
        for parishioner in all_parishioners:
            was_present = Attendance.objects.filter(
                parishioner=parishioner,
                date=mass_date,
                event__isnull=True  # Mass-only attendance
            ).exists()

            if not was_present:
                absentee_summary.append({
                    'name': f"{parishioner.user.first_name} {parishioner.user.last_name}",
                    'date': mass_date,
                    'type': "Sunday Mass"
                })

    # Process event-based attendance (strictly per event)
    unique_events = Attendance.objects.filter(event__isnull=False).values('date', 'event').distinct()

    for entry in unique_events:
        event_date = entry['date']
        event_id = entry['event']
        event_obj = Event.objects.get(pk=event_id)

        for parishioner in all_parishioners:
            was_present = Attendance.objects.filter(
                parishioner=parishioner,
                date=event_date,
                event_id=event_id
            ).exists()

            if not was_present:
                absentee_summary.append({
                    'name': f"{parishioner.user.first_name} {parishioner.user.last_name}",
                    'date': event_date,
                    'type': f"Event: {event_obj.name}"
                })

    return render(request, 'faithlink/attendance_history.html', {
        'morning_mass': morning_mass,
        'afternoon_mass': afternoon_mass,
        'evening_mass': evening_mass,
        'event_attendance': event_attendance,
        'absentee_summary': absentee_summary
    })

from django.http import JsonResponse
from django.db.models import Count
from django.utils.timezone import now
from django.db.models.functions import TruncWeek, TruncMonth
from calendar import monthrange
from collections import defaultdict
import datetime

from django.http import JsonResponse
from django.db.models import Count
from django.utils.timezone import now

from .models import Attendance, Parishioner

def attendance_summary(request):
    filter_type = request.GET.get("filter", "today")   # all | today | month | date
    month = request.GET.get("month")
    date = request.GET.get("date")

    today = now().date()
    queryset = Attendance.objects.filter(status="Present")  # make consistent

    # Apply filters
    if filter_type == "today":
        queryset = queryset.filter(date=today)
    elif filter_type == "month" and month:
        try:
            month_date = datetime.datetime.strptime(month, "%Y-%m")
            queryset = queryset.filter(
                date__year=month_date.year, date__month=month_date.month
            )
        except ValueError:
            pass
    elif filter_type == "date" and date:
        try:
            specific_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(date=specific_date)
        except ValueError:
            pass

    total_attendance = queryset.count()
    total_members = Parishioner.objects.count()
    absentees = max(total_members - total_attendance, 0)

    # Mass type breakdown
    morning_count = queryset.filter(mass_type="Morning").count()
    afternoon_count = queryset.filter(mass_type="Afternoon").count()
    evening_count = queryset.filter(mass_type="Evening").count()
    events_count = queryset.filter(event__isnull=False).count()

    # Highest attendance day
    highest = (
        queryset.values("date")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )
    highest_info = {
        "service": "Overall",
        "date": highest["date"].strftime("%Y-%m-%d") if highest else "",
        "count": highest["count"] if highest else 0,
    }

    # Attendance rate (based on distinct service days)
    if filter_type == "month" and month:
        service_days = queryset.values("date").distinct().count()
        month_total_members = total_members * service_days
        attendance_rate = (
            round((total_attendance / month_total_members) * 100, 2)
            if month_total_members > 0
            else 0
        )
        current_month = month_date.strftime("%B")
    else:
        attendance_rate = (
            round((total_attendance / total_members) * 100, 2)
            if total_members > 0
            else 0
        )
        current_month = today.strftime("%B")

    latest_date = queryset.order_by("-date").first().date.strftime("%Y-%m-%d") if queryset.exists() else ""

    return JsonResponse({
        "total_attendance": total_attendance,
        "absentees": absentees,
        "morning": morning_count,
        "afternoon": afternoon_count,
        "evening": evening_count,
        "events": events_count,
        "highest": highest_info,
        "attendance_rate": attendance_rate,
        "current_month": current_month,
        "latest_date": latest_date,
    })


def attendance_over_time(request):
    month = request.GET.get("month", None)
    qs = Attendance.objects.filter(status="Present")

    labels, values = [], []

    if month:
        # Filter for that month
        year, month_num = map(int, month.split("-"))
        start = datetime.date(year, month_num, 1)
        end = datetime.date(year, month_num, monthrange(year, month_num)[1])
        qs = qs.filter(date__range=[start, end])

        # Group by day
        grouped = qs.values("date").annotate(count=Count("id")).order_by("date")
        labels = [g["date"].strftime("%b %d") for g in grouped]
        values = [g["count"] for g in grouped]

    else:
        # Default: group by week for current year
        grouped = qs.annotate(week=TruncWeek("date")).values("week").annotate(count=Count("id")).order_by("week")
        labels = [g["week"].strftime("Week %U") for g in grouped]  # %U starts with Sunday, clearer for attendance
        values = [g["count"] for g in grouped]

    return JsonResponse({"labels": labels, "values": values})




def get_parishioner_count(request):
    count = CustomUser.objects.filter(is_parishioner=True).count()
    return JsonResponse({"count": count})

def get_prayerrequest_count(request):
    count = PrayerRequest.objects.count()
    return JsonResponse({"count": count})



@login_required
def user_attendance_history(request):
    # Get the parishioner associated with the current user
    parishioner = get_object_or_404(Parishioner, user=request.user)

    # Get all attendance records for the logged-in user's parishioner profile
    attendance_records = Attendance.objects.filter(parishioner=parishioner).select_related('event').order_by('-date')

    # Filter by type
    morning_mass = attendance_records.filter(mass_type="Morning", event__isnull=True)
    afternoon_mass = attendance_records.filter(mass_type="Afternoon", event__isnull=True)
    evening_mass = attendance_records.filter(mass_type="Evening", event__isnull=True)
    event_attendance = attendance_records.filter(event__isnull=False)

    return render(request, 'faithlink/MyAttendance.html', {
        'morning_mass': morning_mass,
        'afternoon_mass': afternoon_mass,
        'evening_mass': evening_mass,
        'event_attendance': event_attendance,
    })


def attendance_view(request):
    events = Event.objects.filter(date__gte=timezone.now())
    return render(request, 'faithlink/attendance.html', {'events': events})

@api_view(['GET'])
def get_upcoming_events(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    data = [{'id': event.id, 'name': event.name, 'date': event.date.strftime('%Y-%m-%d %H:%M')} for event in events]
    return Response(data)



def detect_mass_type():
    current_time = localtime()  # Converts to active timezone
    hour = current_time.hour
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour <= 23:
        return "Evening"
    return "Morning"  # Default fallback





@api_view(['POST'])
def mark_attendance_event(request):
    # Extract parishioner custom ID
    parishioner_custom_id = request.data.get('parishioner_id')
    if not parishioner_custom_id:
        return Response({"error": "Parishioner ID is required."}, status=400)

    # Retrieve parishioner using custom ID
    try:
        parishioner = Parishioner.objects.get(parishioner_id=parishioner_custom_id)
    except Parishioner.DoesNotExist:
        return Response({"error": "Parishioner not found."}, status=404)

    event_id = request.data.get('event_id')
    auto_mass = request.data.get('auto_mass', False)

    # Retrieve event if applicable
    event = None
    if event_id and not auto_mass:
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=404)

    # Detect mass type if auto_mass is True
    mass_type = detect_mass_type() if auto_mass else None

    # Mark attendance
    attendance, created = Attendance.objects.get_or_create(
        parishioner=parishioner,
        date=timezone.now().date(),
        event=event,
        defaults={
            'status': 'Present',
            'mass_type': mass_type
        }
    )

    if not created:
        return Response({"message": "Attendance already marked."}, status=200)

    # Construct response message
    response_message = "Attendance recorded"
    if mass_type:
        response_message += f" for {mass_type} Mass"
    elif event:
        response_message += f" for event: {event.name}"

    return Response({"message": response_message}, status=201)



# --- Viewsets & Class-based views ---

class ParishionerViewSet(viewsets.ModelViewSet):
    queryset = Parishioner.objects.all()
    serializer_class = ParishionerSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(is_parishioner=False, is_superuser=False)
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def approve_parishioner(self, request, pk=None):
        user = self.get_object()
        if not request.user.is_staff:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        user.is_parishioner = True
        user.save()

        if not hasattr(user, 'parishioner'):
            parishioner = Parishioner.objects.create(
                user=user,
                name=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                contact=user.phone_number,
                address=user.address,
                birthdate=user.birthdate  
            )
        else:
            parishioner = user.parishioner
            parishioner.birthdate = user.birthdate  

        parishioner.save()
        return Response({'status': 'approved', 'parishioner_id': parishioner.id}, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        return {'request': self.request}


from django.utils.timezone import now
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        # Return only future or ongoing events (date today or later)
        return Event.objects.filter(date__gte=now()).order_by('date')


# class DonationViewSet(viewsets.ModelViewSet):
#     queryset = Donation.objects.select_related('donor').all().order_by('-date')
#     serializer_class = DonationSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         try:
#             parishioner = Parishioner.objects.get(user=self.request.user)
#         except Parishioner.DoesNotExist:
#             raise serializers.ValidationError("No parishioner profile linked to this user.")
        
#         serializer.save(donor=parishioner)
# from rest_framework import serializers


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.select_related('donor').all().order_by('-date')
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            # Try to auto-link parishioner based on current user
            parishioner = Parishioner.objects.get(user=user)
            serializer.save(donor=parishioner)
        except Parishioner.DoesNotExist:
            # Fall back to manually specified donor (e.g., for admin use)
            donor_id = self.request.data.get('donor')
            if not donor_id:
                raise serializers.ValidationError("Donor must be specified.")
            try:
                parishioner = Parishioner.objects.get(id=donor_id)
            except Parishioner.DoesNotExist:
                raise serializers.ValidationError("Selected donor is invalid.")
            serializer.save(donor=parishioner)



from rest_framework.decorators import api_view, permission_classes
from .models import Donation
from .serializers import DonationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_donations(request):
    try:
        parishioner = Parishioner.objects.get(user=request.user)
        donations = Donation.objects.filter(donor=parishioner)
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)
    except Parishioner.DoesNotExist:
        return Response([], status=200)



class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            parishioner = Parishioner.objects.get(user=request.user)
            serializer = ParishionerSerializer(parishioner)
            return Response(serializer.data)
        except Parishioner.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

class FundraisingCampaignViewSet(viewsets.ModelViewSet):
    queryset = FundraisingCampaign.objects.all()
    serializer_class = FundraisingCampaignSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class PrayerRequestViewSet(viewsets.ModelViewSet):
    queryset = PrayerRequest.objects.all()
    serializer_class = PrayerRequestSerializer

    def perform_create(self, serializer):
        serializer.save(parishioner=self.request.user)


from rest_framework import viewsets, permissions
from .models import SacramentRecord
from .serializers import SacramentRecordSerializer

class SacramentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = SacramentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SacramentRecord.objects.all()
        parishioner_id = self.request.query_params.get('parishioner_id')
        if parishioner_id:
            queryset = queryset.filter(parishioner_id=parishioner_id)
        # else: do NOT filter, return all records
        return queryset

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class MySacramentRecordViewSet(viewsets.ModelViewSet):
    queryset = SacramentRecord.objects.all()
    serializer_class = SacramentRecordSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my')
    def my_records(self, request):
        parishioner = getattr(request.user, 'parishioner', None)
        if not parishioner:
            return Response([], status=200)
        queryset = self.queryset.filter(parishioner=parishioner)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @action(detail=True, methods=['post'], url_path='request_certificate')
    def request_certificate(self, request, pk=None):
        record = self.get_object()
        # Mark as requested
        record.certificate_requested = True
        record.save()

        return Response({"message": "Certificate request submitted."}, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['get'], url_path='certificate')
    def certificate(self, request, pk=None):
        record = self.get_object()
        parishioner = record.parishioner

        # (reuse your PDF generation code here)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        # ... draw certificate same as in IndividualCertificatePDFView ...
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf')





class IndividualCertificatePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        parishioner = getattr(user, 'parishioner', None)

        if not parishioner:
            return HttpResponse("No parishioner record found.", status=404)

        record = get_object_or_404(SacramentRecord, pk=pk, parishioner=parishioner)

        # Sacrament-specific formal message
        sacrament_statements = {
            'Baptism': "This certifies that the recipient has been cleansed by the holy waters of Baptism and welcomed into the family of God.",
            'Confirmation': "This certifies the sealing of the Holy Spirit in the recipient's life, affirming faith and spiritual strength.",
            'First Communion': "This certifies the sacred participation in the Eucharist, receiving the Body and Blood of Christ for the first time.",
            'Marriage': "This certifies the holy union of love and commitment under the sacrament of Matrimony in the presence of God.",
            'Ordination': "This certifies the reception of Holy Orders, dedicating one’s life to the service of God and His Church.",
            'Anointing of the Sick': "This certifies the sacred anointing of the recipient with grace, healing, and peace in times of physical or spiritual need."
        }
        statement = sacrament_statements.get(record.sacrament, "This certifies that the recipient has received a sacrament of the Holy Church.")

        # PDF setup
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Layout config
        border_margin = 40
        content_margin = 60
        line_height = 20

        # Draw background
        background_path = os.path.join('static', 'images', 'avatar.png')  # Customize as needed
        if os.path.exists(background_path):
            bg = ImageReader(background_path)
            p.drawImage(bg, 0, 0, width=width, height=height, mask='auto')

        # Border
        p.setStrokeColor(colors.HexColor('#444'))
        p.setLineWidth(4)
        p.rect(border_margin, border_margin, width - 2 * border_margin, height - 2 * border_margin)

        # Title
        p.setFont("Helvetica-Bold", 26)
        p.setFillColor(colors.HexColor("#2c3e50"))
        p.drawCentredString(width / 2, height - content_margin - 20, f"Certificate of {record.sacrament}")

        # Church name
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.black)
        p.drawCentredString(width / 2, height - content_margin - 60, "FaithLink Parish Community")

        # Recipient name
        full_name = f"{parishioner.first_name} {parishioner.last_name}".upper()

        # Optional underline
        p.setLineWidth(1)  # Thin underline
        name_width = p.stringWidth(full_name, "Helvetica-Bold", 16)
        p.line(
            (width - name_width) / 2,
            height - content_margin - 140,
            (width + name_width) / 2,
            height - content_margin - 140
        )
        p.setLineWidth(4)  # Reset back to original border thickness if needed later

        # Line 1: Introduction
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - content_margin - 100, "This Certificate is given to:")

        # Line 2: Full Name (larger, bolder, slightly below)
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - content_margin - 135, full_name)



       # Formal statement (centered & manually wrapped)
        statement_lines = textwrap.wrap(statement, width=90)

        p.setFont("Helvetica-Oblique", 12)
        y_position = height - content_margin - 170

        for line in statement_lines:
            p.drawCentredString(width / 2, y_position, line)
            y_position -= 18



        # Sacrament info
        y_pos = height - content_margin - 220
        p.setFont("Helvetica", 12)
        p.drawCentredString(width / 2, y_pos, f"Received on {record.date_received.strftime('%B %d, %Y')} at {record.place_received}")
        y_pos -= line_height
        p.drawCentredString(width / 2, y_pos, f"Officiated by: {record.officiant}")

        # Notes
        if record.notes:
            y_pos -= line_height
            p.setFont("Helvetica-Oblique", 10)
            p.drawCentredString(width / 2, y_pos, f"Note: {record.notes}")

        # Signatures
        p.setFont("Helvetica", 12)
        p.drawString(content_margin, border_margin + 60, "_______________________")
        p.drawString(content_margin + 20, border_margin + 45, "Parish Priest")

        p.drawString(width - content_margin - 180, border_margin + 60, "_______________________")
        p.drawString(width - content_margin - 160, border_margin + 45, "Parish Seal")

 
        # Date of Issue
        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, border_margin + 30, f"Issued on: {datetime.date.today().strftime('%B %d, %Y')}")

        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf')


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.select_related('parishioner', 'event')

        parishioner_id = self.request.query_params.get('parishioner')
        event_id = self.request.query_params.get('event')
        date_filter = self.request.query_params.get('date')

        if parishioner_id: 
            queryset = queryset.filter(parishioner_id=parishioner_id)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset.order_by('-date', '-time')

# --- End of views.py ---
