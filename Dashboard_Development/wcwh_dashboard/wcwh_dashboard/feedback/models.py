from django.db import models
import json
#from django.contrib.postgres.fields import JSONField


# Create your models here.

class Participant(models.Model):
	participant_id = models.CharField(max_length=100)

class Measurements(models.Model):
	participant_id = models.ForeignKey(Participant,on_delete=models.CASCADE)
	measurement_datetime = models.DateTimeField()
	measurement_type = models.CharField(max_length=100)
	measurement_value = models.TextField()

	class Meta:
		unique_together = ('participant_id', 'measurement_datetime', 'measurement_type')

	@classmethod
	def add_measurement(cls, participant_id, measurement_datetime, measurement_type, measurement_value_dict):
		'''
		Adds a measurement to the model
		'''
		participant = Participant.objects.get(participant_id = participant_id)

		measurement = {'participant_id':participant,
			'measurement_datetime':measurement_datetime,
			'measurement_type':measurement_type,
			'measurement_value':json.dumps(measurement_value_dict, indent=4)
		}

		return cls.objects.create(**measurement)

	@classmethod
	def update_measurement(cls, participant_id, measurement_datetime, measurement_type, measurement_value_dict):
		'''
		Updates an existing measurement
		'''
		if not cls.objects.filter(participant_id = participant_id,
			measurement_datetime = measurement_datetime,
			measurement_type = measurement_type).exists():

			measurement = cls.add_measurement(participant_id, measurement_datetime, measurement_type, measurement_value_dict)
		else:
			measurement = cls.objects.get(participant_id = participant_id,
				measurement_datetime = measurement_datetime,
				measurement_type = measurement_type)

			measurement['measurement_value'] = json.dumps(measurement_value_dict, indent=4)

			measurement.save()

		return measurement		


