# views.py

# --- Imports ---
import json
from datetime import date
from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


# --- Function-based views ---


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from .models import Event

@login_required
def dashboard_view(request):
    context = get_parishionerSignup(request.user)

    # Add upcoming events
    context['upcoming_events'] = Event.objects.filter(date__gte=now()).order_by('date')[:5]

    # Add dummy or dynamic birthday/anniversary data (replace with real logic later)
    context['birthdays'] = [
        {"name": "Anna Dela Cruz", "date": "June 10"},
        {"name": "Mark Santos", "date": "June 12"},
    ]

    context['anniversaries'] = [
        {"name": "John & Maria", "date": "June 15"},
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

# def attendance_view(request):
#     context = get_parishionerSignup(request.user)
#     return render(request, 'faithlink/attendance.html', context)


from django.utils import timezone

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

from django.shortcuts import render
from .models import Attendance

def attendance_history(request):
    # Fetch all attendance records
    attendance_records = Attendance.objects.select_related('parishioner__user').order_by('-date')

    # Categorize attendance records
    morning_mass = attendance_records.filter(mass_type="Morning", event__isnull=True)
    afternoon_mass = attendance_records.filter(mass_type="Afternoon", event__isnull=True)
    evening_mass = attendance_records.filter(mass_type="Evening", event__isnull=True)

    # Separate event-based attendance
    event_attendance = attendance_records.filter(event__isnull=False)

    return render(request, 'faithlink/attendance_history.html', {
        'morning_mass': morning_mass,
        'afternoon_mass': afternoon_mass,
        'evening_mass': evening_mass,
        'event_attendance': event_attendance,
    })

def get_parishioner_count(request):
    count = CustomUser.objects.filter(is_parishioner=True).count()
    return JsonResponse({"count": count})

def get_prayerrequest_count(request):
    count = PrayerRequest.objects.count()
    return JsonResponse({"count": count})

from django.utils import timezone
from datetime import date
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from .models import Event, Attendance, Parishioner


def attendance_view(request):
    events = Event.objects.filter(date__gte=timezone.now())
    return render(request, 'faithlink/attendance.html', {'events': events})

@api_view(['GET'])
def get_upcoming_events(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    data = [{'id': event.id, 'name': event.name, 'date': event.date.strftime('%Y-%m-%d %H:%M')} for event in events]
    return Response(data)


from django.utils.timezone import localtime

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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Parishioner, Event, Attendance


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
            )
        else:
            parishioner = user.parishioner

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


from rest_framework import viewsets
from django.utils.timezone import now
from .models import Event
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        # Return only future or ongoing events (date today or later)
        return Event.objects.filter(date__gte=now()).order_by('date')


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.select_related('donor').all().order_by('-date')
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

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
        parishioner = Parishioner.objects.get(user=self.request.user)
        serializer.save(parishioner=parishioner)

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

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

class MySacramentRecordViewSet(viewsets.ModelViewSet):
    queryset = SacramentRecord.objects.all()
    serializer_class = SacramentRecordSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my')
    def my_records(self, request):
        # Assumes user is linked to a Parishioner instance
        parishioner = getattr(request.user, 'parishioner', None)
        if not parishioner:
            return Response([], status=200)
        queryset = self.queryset.filter(parishioner=parishioner)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SacramentRecord

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SacramentRecord


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SacramentRecord
import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SacramentRecord
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import datetime
import os
import textwrap



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
