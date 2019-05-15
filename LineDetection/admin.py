from django.contrib import admin

# Register your models here.

from .models import Facility, Energy, Anomaly

admin.site.register(Facility)
admin.site.register(Energy)
admin.site.register(Anomaly)