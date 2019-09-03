# Import for command modules
from django.core.management.base import BaseCommand, CommandError
# Import of django models
from pm.models import PM as pm

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
        import_success = True
        if options['var_id'] == 'thermal':
            df_hourly, df_daily, srs_hourly, srs_daily = lf.importThermalConditions(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported thermal condtions (T/RH) data'))
        elif options['var_id'] == 'iaq':
            df_hourly, df_daily, df_nightly, srs_hourly, srs_daily, srs_hourly_nightly, srs_nightly = lf.importIAQ(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported IAQ data'))
        elif options['var_id'] == 'sleep':
            df_hourly, df_daily, srs_hourly, srs_daily = lf.importThermalConditions(data_dir + '/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported sleep quality data'))
        else:
            self.stdout.write(self.style.WARNING('WARNING: INCORRECT IMPORT ARGUMENT\n\nInclude one of the following (list is exhaustive):\n\t- thermal\n\t- iaq\n\t- sleep_stages\n\t -sleep_surveys'))
            import_success = False

        # Store data in models
        if import_success:
            pass