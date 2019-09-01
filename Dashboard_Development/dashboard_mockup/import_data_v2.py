import sys, os
from pm.models import PM
import pandas
import lambda_thermal

# Full path to django project directory
your_djangoproject_home="/~/Google\ Drive/Research/5_Sensors/Projects/UT2000-SummerDashboard/Dashboard_Development/"

import sys, os
sys.path.append(your_djangoproject_home) 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

df1, df2, s1, s2 = lambda_thermal.lambdaThermalConditions()
