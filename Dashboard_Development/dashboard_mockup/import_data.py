
# Full path and name to your csv file
csv_filepathname="/~/Google\ Drive/Research/5_Sensors/Projects/UT2000-SummerDashboard/Code_Development/Files/uynulntv_IAQ.csv"

# Full path to your django project directory
your_djangoproject_home="/~/Google\ Drive/Research/5_Sensors/Projects/UT2000-SummerDashboard/Dashboard_Development/"

import sys, os
sys.path.append(your_djangoproject_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from pm.models import PM
import csv
import pandas

dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
for row in dataReader:
	if row[0] != 'Month': 
	# Ignore the header row, import everything else
		pm = PM()
		pm.concentrations = row[3]
		pm.aqi = row[4]
		pm.measurement_time = row[5]

pm.save()