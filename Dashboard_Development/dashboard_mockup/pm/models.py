from django.db import models

import datetime

# Parent class to link all the databases together
class ID_Label(models.Model):
	name = models.CharField('name/label/id of the subject',max_length=20)

# Data children classes

## Thermal Conditions
class Thermal(models.Model):
	id_label = models.ForeignKey(ID_Label,on_delete=models.CASCADE)
	name = models.CharField('name/label/id of the subject',max_length=20)
	temperature = models.FloatField()
	rh = models.FloatField()
	measurement_time = models.DateTimeField()

## Particulate Matter
class PM(models.Model):
	id_label = models.ForeignKey(ID_Label,on_delete=models.CASCADE)
	name = models.CharField('name/label/id of the subject',max_length=20)
	concentration = models.FloatField()
	aqi = models.FloatField('air quality index')
	measurement_time = models.DateTimeField()

## Sleep Stages
class SleepMetrics(models.Model):
	id_label = models.ForeignKey(ID_Label,on_delete=models.CASCADE)
	name = models.CharField('name/label/id of the subject',max_length=20)
	time_asleep = models.FloatField('minutes spent in REM or Non-REM')
	awake = models.FloatField('percentage of time spent awake')
	rem = models.FloatField('percentage of time spent in REM')
	nrem = models.FloatField('percentage of tiem spent in Non-REM')
	latency = models.FloatField('number of minutes awake before falling asleep')
	efficiency = models.FloatField('percentage of time spent asleep while in bed')
	night = models.DateTimeField()
	count = models.IntegerField('number of datapoints averaged to create the metrics')

## Sleep Stages
class SleepSurveys(models.Model):
	id_label = models.ForeignKey(ID_Label,on_delete=models.CASCADE)
	name = models.CharField('name/label/id of the subject',max_length=20)
	time_asleep = models.FloatField('minutes spent in REM or Non-REM')
	restful = models.IntegerField('Likert Scale value for how restful the user thought their sleep was')
	refreshed = models.IntegerField('Likert Scale value for how refreshed the user thought their sleep was')
	aggregate = models.FloatField('Sum of time_asleep, restful score, and refreshed score')
	normalized = models.FloatField('Normalized sleep score')
	night = models.DateTimeField()
	count = models.IntegerField('number of datapoints averaged to create the metrics')

