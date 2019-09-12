from django.shortcuts import render
from django.http import HttpResponse
from feedback.models import *
from django.forms.models import model_to_dict
from django.core import serializers
from datetime import datetime
import json

def index(request):
	return HttpResponse("Hello World")

def measurement_query(request):
	if request.GET:
		query = {}
		if "participant_id" in request.GET and request.GET['participant_id']:
			if not Participant.objects.filter(participant_id=request.GET['participant_id']).exists():
				return HttpResponse('Could not find participant {}'.format(request.GET['participant_id']),status_code=404)
			
			participant = Participant.objects.get(participant_id=request.GET['participant_id'])
			query['participant_id'] = participant
			if 'start_time' in request.GET and request.GET['start_time']:
				query['measurement_datetime__gte'] = request.GET['start_time']
			if 'end_time' in request.GET and request.GET['end_time']:
				query['measurement_datetime__lte'] = request.GET['end_time']
			measurements = Measurements.objects.filter(**query)
			#return HttpResponse(json.dumps(model_to_dict(participant)))
			return HttpResponse(serializers.serialize('json',measurements))
		else:
			return HttpResponse('Query requires a participant id',status_code=400)
	else:
		return HttpResponse('Does not accept POST methods',status_code=405)