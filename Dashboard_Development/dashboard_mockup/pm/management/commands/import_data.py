from django.core.management.base import BaseCommand, CommandError
from pm.models import PM as pm
import pandas as pd
import numpy as np

import sys, os
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import lambda_functions as lf

class Command(BaseCommand):
    help = 'Imports data into the models'

    def add_arguments(self, parser):
        parser.add_argument('var_id', type=str)

    def handle(self, *args, **options):
        if options['var_id'] == 'thermal':
            df1, df2, s1, s2 = lf.lambdaThermalConditions(file_dir + '/data/')
            self.stdout.write(self.style.SUCCESS('Succesfully imported thermal data'))
            # Store data in models
        else:
            self.stdout.write(self.style.WARNING('Incorrect input parameter. Try one of:\n\t-thermal\n\t-iaq'))
