from django.contrib import admin
from .models import Parishioner, Event, Donation,Attendance, SacramentRecord
from accounts.models import CustomUser
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Parishioner)
admin.site.register(Event)
admin.site.register(Donation)
admin.site.register(Attendance)
admin.site.register(SacramentRecord)

