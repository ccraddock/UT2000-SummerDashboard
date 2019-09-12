from django.contrib import admin

# Register your models here.
from .models import Participant, Measurements

admin.site.register(Participant)
admin.site.register(Measurements)