from django.db import models

import datetime

# Create your models here.
class PM(models.Model):
	concentration = models.FloatField()
	aqi = models.FloatField('air quality index')
	measurement_time = models.DateTimeField()