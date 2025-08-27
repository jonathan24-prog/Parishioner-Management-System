from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# View imports
from .views import (
    dashboard_view, attendance_view, attendance_history, UserProfileView, 
    sacramentals_view_user, attendance_scan_view, 
    generate_parishioner_qr, AttendanceViewSet, SacramentRecordViewSet, 
    LandingPage_view, PrayerRequestViewSet, get_prayerrequest_count, 
    prayer_request_view, FundraisingCampaignViewSet, MyProfileAPIView, 
    profile, events_view_user, editparishioner, EventViewSet, DonationViewSet, 
    parishioners_view, get_parishioner_count, parishionersReq_view, 
    events_view, financial_view, sacramentals_view, ParishionerViewSet, 
    CustomUserViewSet,get_upcoming_events,mark_attendance_event,MyQr_view,MySacramentRecordViewSet,
    IndividualCertificatePDFView, user_attendance_history,privacy_policy, user_donation_view,
    user_donations, receipt_view, attendance_summary, attendance_over_time, groups_view,GroupViewSet,
    groups_view_user
)

# DRF Router setup
router = DefaultRouter()
router.register(r'parishioners', ParishionerViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'customusers', CustomUserViewSet)
router.register(r'events', EventViewSet, basename='events')
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'fundraising-campaigns', FundraisingCampaignViewSet)
router.register(r'prayer-requests', PrayerRequestViewSet)
router.register(r'sacrament-records', SacramentRecordViewSet, basename='sacrament-records')
router.register(r'attendance', AttendanceViewSet)
router.register(r'sacrament-record', MySacramentRecordViewSet, basename='sacramentrecord')


# URL patterns
urlpatterns = [
    path('', LandingPage_view, name='LandingPage'),

    # API routes
    path('api/', include(router.urls)),
    # path('api/mark-attendance/', mark_attendance, name='mark_attendance'),
    path('api/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/my-profile/', MyProfileAPIView.as_view(), name='my-profile'),

    # Count endpoints
    path('customusers/count/', get_parishioner_count, name='get_parishioner_count'),
    path('prayer-request/count/', get_prayerrequest_count, name='get_prayerRequest_count'),

    # Admin-related
    path('admin/scan-attendance/', attendance_scan_view, name='attendance_scan'),

    # Dashboard & profile
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile, name='profile'),

    # Parishioner-related
    path('parishioners/', parishioners_view, name='parishioners'),
    path('parishionersReq/', parishionersReq_view, name='parishionersReq'),
    path('editparishioner/<int:pk>', editparishioner, name='editparishioner'),
    path('parishioner/qr/', generate_parishioner_qr, name='generate_parishioner_qr'),

    # groups
    path('groups/', groups_view, name='groups'),
    path('groups_user/', groups_view_user, name='groups_user'),

    # Events
    path('events/', events_view, name='events'),
    path('events-user/', events_view_user, name='events_user'),
    path('api/events/', get_upcoming_events, name='api-events'),
    
     # Events
    path('QRview/', MyQr_view, name='QRview'),
 
    # privacy and policy
    path('privacy/', privacy_policy, name='privacy_policy'),
 

    # Attendance
    path('attendance/', attendance_view, name='attendance'),
    path('history/', attendance_history, name='attendance-history'),
    path('api/mark-attendance/', mark_attendance_event, name='mark-attendance'),
    path('my-attendance/', user_attendance_history, name='user_attendance_history'),
    path('attendance/summary/', attendance_summary, name='attendance_summary'),
    path('attendance/over-time/', attendance_over_time, name='attendance_over_time'),

    # Sacramentals
    path('Sacramentals/', sacramentals_view, name='sacramentals'),
    path('Sacramentals-user/', sacramentals_view_user, name='sacramentals_User'),
    path('sacrament-record/<int:pk>/certificate/', IndividualCertificatePDFView.as_view(), name='sacrament-certificate'),


    

    # Prayer requests
    path('prayer-requests/', prayer_request_view, name='prayer_request'),

    # Financial
    path('financial-Management/', financial_view, name='financial_management'),
    path('donate/', user_donation_view, name='user-donation'),
    path('donations/user/', user_donations, name='user-donations'),
    path('donations/receipt/<int:pk>/', receipt_view, name='receipt_view'),



    # Accounts app
    path('accounts/', include('accounts.urls')),
]

# Static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
