from django.db import models

import datetime

# Create your models here.
class PM(models.Model):
	name = models.CharField('name/label/id of the subject',max_length=20)
	concentration = models.FloatField()
	aqi = models.FloatField('air quality index')
	measurement_time = models.DateTimeField()