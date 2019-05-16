from django.contrib import admin

# Register your models here.

from .models import Facility, Energy, Anomaly, season_goal, production_amount

admin.site.register(Facility)
admin.site.register(Energy)
admin.site.register(Anomaly)
admin.site.register(season_goal)
admin.site.register(production_amount)