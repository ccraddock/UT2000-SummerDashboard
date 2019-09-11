# Import for command modules
from django.core.management.base import BaseCommand, CommandError
# Import of django models
from pm.models import ID_Label
from pm.models import PM
from pm.models import Thermal
from pm.models import SleepMetrics
from pm.models import SleepSurveys

# Import of python data modules
import pandas as pd
import numpy as np

# Import of necessary OS modules
import sys, os
## Gets the path to this current directory and adds it to the path
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
## Gets the path to the data directory and adds it to the path
data_dir = os.path.dirname('/Users/hagenfritz/Google Drive/Research/5_Sensors/Projects/UT2000-SummerDashboard/Code_Development/Data/')
sys.path.append(data_dir)

# Imports the lambda functions
import lambda_functions as lf

class Command(BaseCommand):
    help = 'Imports data into the models'

    def add_arguments(self, parser):
        parser.add_argument('var_id', type=str)

    def handle(self, *args, **options):
        if options['var_id'] == 'thermal':
            ## Importing data via lambda functions
            df_hourly, df_daily, srs_hourly, srs_daily = lf.importThermalConditions(data_dir + '/')
            print(df_hourly.head())
            print(srs_hourly[0].head())
            self.stdout.write(self.style.SUCCESS('Succesfully imported thermal condtions (T/RH) data'))
            ## Putting data into models
            for name in srs_hourly.index:
                ### ID model
                ID = ID_Label(name=name)
                ID.save()     
                self.stdout.write(self.style.SUCCESS('Succesfully saved ID to database'))
                data = srs_hourly[name]
                for i in range(len(data)):
                    ### Thermal model
                    thermal = Thermal(id_label=ID,
                        name=name,
                        temperature=data['Temperature(F)'][i],
                        rh=data['Relative Humidity'][i],
                        measurement_time=data.index[i])
                    thermal.save()
            self.stdout.write(self.style.SUCCESS('Succesfully saved thermal data to database'))

        elif options['var_id'] == 'iaq':
            df_hourly, df_daily, df_nightly, srs_hourly, srs_daily, srs_hourly_nightly, srs_nightly = lf.importIAQ(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported IAQ data'))
        elif options['var_id'] == 'sleep_metrics':
            df_nightly, srs_stages, srs_metrics = lf.importSleepMetrics(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported sleep stage data from Fitbit'))
        elif options['var_id'] == 'sleep_surveys':
            df_nightly, srs_nightly = lf.importSleepSurveys(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported sleep survey data from Beiwe'))
        else:
            self.stdout.write(self.style.WARNING('WARNING: INCORRECT IMPORT ARGUMENT\n\nInclude one of the following (list is exhaustive):\n\t- thermal\n\t- iaq\n\t- sleep_metrics\n\t -sleep_surveys'))
            