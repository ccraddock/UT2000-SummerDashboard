import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import sys, os

# --------------------- #
# Main Lambda Functions #
# --------------------- #

# Thermal Conditions #
# ------------------------------------------------------------------------- #
def importThermalConditions(DIR, starting='03/11/2019', ending='04/15/2019'):
    '''
    Inputs:
        - DIR: path to where the data is located
        - starting: string representing the first date to use in the data range
        - ending: string representing the last date to use in the data range
    Returns two dataframes and two series of dataframes:
        - df of averaged values for temperature and relative humidity across all users by HOUR
        - df of averaged values for temperature and relative humdidity across all users by DAY
        - series with dataframes for each individual with data at each HOUR
        - series with dataframes for each individual with data at each DAY

    '''

    raw_data = pd.DataFrame() # Stores all data
    id_list = []
    # Hagen's local directory

    # Importing the data
    for folder in os.listdir(DIR):
        ## Checking for any hidden files 
        if folder[0] != '.':
            id_list.append(folder) # Adding the ID to the list
            temp = pd.DataFrame() # Stores one csv file's worth of data
            file_dir = DIR + folder + '/beacon_data/bevo/sht31d/' # Location of file

            ## Looping through all the files in the sensor directory
            for file in os.listdir(file_dir):
                if str(file[-3:]) == 'csv': # To ensure that we only read in csv files
                    temp = pd.read_csv(file_dir + file,header=None,names=['Time','Relative Humidity','Temperature(C)'])
                    temp['ID'] = folder # Storing the ID for each data entry
                    raw_data = pd.concat([raw_data,temp],axis=0,ignore_index=True) # Concatenating to the overall DataFrame

    ## Creating a date array for indexing that converts utctimestamp to Central Time
    raw_data = raw_data.dropna() # Dropping any NaNs
    t = np.zeros((len(raw_data)),dtype='datetime64[ns]') # Array to store times
    for j in range(len(t)):
        ts = int(raw_data['Time'].values[j])
        t[j] = datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)

    ## Re-indexing and re-naming
    raw_data['Time'] = t
    raw_data = raw_data.set_index('Time') # Setting time as the dataframe index
    raw_data = raw_data.sort_index()

    ## Adding column for temperature in Farenheit for us Americans
    raw_data['Temperature(F)'] = raw_data['Temperature(C)']*1.8+32

    ## Removing data from DF that isn't in the deployment range
    start_date = datetime.strptime(starting, '%m/%d/%Y') # converting input to datetime
    end_date = datetime.strptime(ending, '%m/%d/%Y') # converting input to datetime
    ### Checking to see if there is data in the range
    if raw_data.index[-1] < start_date:
        print('\tNo data from this deployment range')

    ## Checking to see if we are importing one day's worth of data
    elif start_date == end_date:
        raw_data = raw_data[raw_data.index.month == start_date.month] # mask by month
        raw_data = raw_data[raw_data.index.day == start_date.day] # mask by the day

    ## Normal range of data
    else:
        raw_data = raw_data[start_date:end_date]
    
    # -------------------- #
    # Daily Aggregate Data #
    # -------------------- # 

    # Getting new columns to group by
    raw_data['Month'] = raw_data.index.month
    raw_data['Day'] = raw_data.index.day

    daily_mean = raw_data.groupby(['Month','Day']).mean() # Mean for each day
    daily_count = raw_data.groupby(['Month','Day']).count()
    daily_dates = [] # list to hold dates
    # Converting separate date columns to single datetime entry
    for i in range(len(daily_mean)):
        daily_dates.append(datetime(start_date.year,daily_mean.index[i][0],daily_mean.index[i][1]))
    daily_mean['Date'] = daily_dates # Attaching new column
    daily_mean['Count'] = daily_count['Relative Humidity'] # Adding number of values used to average values
    #daily_mean.to_csv('Files/Aggregate_ThermalConditions_Daily.csv')

    # ---------------- #
    # Daily Data by ID #
    # ---------------- #

    daily_mean_byID = pd.Series()
    temp = raw_data.groupby(['ID','Month','Day']).mean() # Mean for each hour for an ID
    # Converting separate date columns to single datetiem entry and writing to csv
    for name in id_list:
        dates = []
        df = temp.loc[name]
        for i in range(len(df)):
            dates.append(datetime(start_date.year,df.index[i][0],df.index[i][1]))
        df['Date'] = dates
        #df.to_csv('Files/' + name + '_ThermalConditions_Hourly.csv')
        df = df.set_index('Date')
        daily_mean_byID[name] = df
    
    # --------------------- #
    # Hourly Aggregate Data #
    # --------------------- # 

    raw_data['Hour'] = raw_data.index.hour
    ## Writing Out Aggregate Data
    hourly_mean = raw_data.groupby(['Month','Day','Hour']).mean() # Mean for each hour
    hourly_count = raw_data.groupby(['Month','Day','Hour']).count()
    hourly_dates = [] # list to hold dates
    ### Converting separate date columns to single datetime entry
    for i in range(len(hourly_mean)):
        hourly_dates.append(datetime(start_date.year,hourly_mean.index[i][0],hourly_mean.index[i][1],hourly_mean.index[i][2]))
    hourly_mean['Date'] = hourly_dates # Attaching new column
    hourly_mean['Count'] = hourly_count['Relative Humidity'] # Adding number of values used to average values
    #hourly_mean.to_csv('Files/Aggregate_ThermalConditions_Hourly.csv')

    # ----------------- #
    # Hourly Data by ID #
    # ----------------- #

    hourly_mean_byID = pd.Series()
    temp = raw_data.groupby(['ID','Month','Day','Hour']).mean() # Mean for each hour for an ID
    ## Converting separate date columns to single datetiem entry and writing to csv
    for name in id_list:
        dates = []
        df = temp.loc[name]
        for i in range(len(df)):
            dates.append(datetime(start_date.year,df.index[i][0],df.index[i][1],df.index[i][2]))
        df['Date'] = dates
        #df.to_csv('Files/' + name + '_ThermalConditions_Hourly.csv')
        hourly_mean_byID[name] = df


    return hourly_mean,daily_mean,hourly_mean_byID,daily_mean_byID

# Indoor Air Quality #
# ----------------------------------------------------------- #
def importIAQ(DIR, starting='03/11/2019', ending='04/15/2019'):
    '''
    Inputs:
        - DIR: path to where the data is located
        - starting: string representing the first date to use in the data range
        - ending: string representing the last date to use in the data range
    Returns three DataFrames and four Series of DataFrames:
        - DataFrame containing HOURLY PM2.5 concentrations aggregated over all users
        - DataFrame contatining DAILY PM2.5 concentrations aggregated over all users
        - DataFrame containing the NIGHTLY PM2.5 concentration summary statistics aggregated over all users
        - Series indexed by user ID containing DataFrames of the HOURLY concentrations 
        - Series indexed by user ID containing DataFrames of the DAILY concentrations
        - Series indexed by user ID containing DataFrames of the HOURLY NIGHTLY concentrations 
        - Series indexed by user ID containing DataFrames of the NIGHTLY summary statistics
    '''

    raw_data = pd.DataFrame()
    id_list = []
    # Importing the data
    for folder in os.listdir(DIR):
        if folder[0] != '.':
            id_list.append(folder)
            ## Important variables
            file_dir = DIR + folder + '/beacon_data/bevo/pms5003/' # Location of file
            temp = pd.DataFrame() # Stores one csv file's worth of data

            ## Looping through all the files in the sensor directory
            for file in os.listdir(file_dir):
                if str(file[-3:]) == 'csv': # To ensure that we only read in csv files
                    temp = pd.read_csv(file_dir + file,header=None,names=['Time','Concentration'],usecols=[0,2])
                    temp['ID'] = folder
                    raw_data = pd.concat([raw_data,temp],axis=0,ignore_index=True)

    ## Creating a date array for indexing that converts utctimestamp to Central Time
    raw_data = raw_data.dropna() # Dropping any NaNs
    t = np.zeros((len(raw_data)),dtype='datetime64[ns]') # Array to store times
    for j in range(len(t)):
        ts = int(raw_data['Time'].values[j])
        t[j] = datetime.strptime(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)

    ## Re-indexing and re-naming
    raw_data['Time'] = t
    raw_data = raw_data.set_index('Time') # Setting time as the dataframe index
    raw_data = raw_data.sort_index()

    ## Adding column for PM2.5 in AQI
    raw_data['AQI'] = getAQI(raw_data['Concentration'])

    ## Removing data from DF that isn't in the deployment range
    start_date = datetime.strptime(starting, '%m/%d/%Y') # converting input to datetime
    end_date = datetime.strptime(ending, '%m/%d/%Y') # converting input to datetime
    ### Checking to see if there is data in the range
    if raw_data.index[-1] < start_date:
        print('\tNo data from this deployment range')

    ## Checking to see if we are importing one day's worth of data
    elif start_date == end_date:
        raw_data = raw_data[raw_data.index.month == start_date.month] # mask by month
        raw_data = raw_data[raw_data.index.day == start_date.day] # mask by the day

    ## Normal range of data
    else:
        raw_data = raw_data[start_date:end_date]

    # -------------------- #
    # Daily Aggregate Data #
    # -------------------- # 

    # Getting new columns to group by
    raw_data['Month'] = raw_data.index.month
    raw_data['Day'] = raw_data.index.day

    daily_mean = raw_data.groupby(['Month','Day']).mean() # Mean for each day
    daily_count = raw_data.groupby(['Month','Day']).count()
    daily_dates = [] # list to hold dates
    # Converting separate date columns to single datetime entry
    for i in range(len(daily_mean)):
        daily_dates.append(datetime(start_date.year,daily_mean.index[i][0],daily_mean.index[i][1]))
    daily_mean['Date'] = daily_dates # Attaching new column
    daily_mean['Count'] = daily_count['Concentration'] # Adding number of values used to average values
    #daily_mean.to_csv('Files/Aggregate_ThermalConditions_Daily.csv')

    # ---------------- #
    # Daily Data by ID #
    # ---------------- #

    daily_mean_byID = pd.Series()
    temp = raw_data.groupby(['ID','Month','Day']).mean() # Mean for each hour for an ID
    # Converting separate date columns to single datetiem entry and writing to csv
    for name in id_list:
        dates = []
        df = temp.loc[name]
        for i in range(len(df)):
            dates.append(datetime(start_date.year,df.index[i][0],df.index[i][1]))
        df['Date'] = dates
        #df.to_csv('Files/' + name + '_ThermalConditions_Hourly.csv')
        df = df.set_index('Date')
        daily_mean_byID[name] = df
        
    # --------------------- #
    # Hourly Aggregate Data #
    # --------------------- # 

    # Getting new columns to group by
    raw_data['Hour'] = raw_data.index.hour
    
    # Writing Out Aggregate Data
    hourly_mean = raw_data.groupby(['Month','Day','Hour']).mean() # Mean for each hour
    hourly_count = raw_data.groupby(['Month','Day','Hour']).count() # Count for each hour
    dates = [] # list to hold dates
    ## Converting separate date columns to single datetime entry
    for i in range(len(hourly_mean)):
        dates.append(datetime(start_date.year,hourly_mean.index[i][0],hourly_mean.index[i][1],hourly_mean.index[i][2]))
    hourly_mean['Date'] = dates # Attaching new column
    hourly_mean['Count'] = hourly_count['Concentration']
    #hourly_mean.to_csv('Files/Aggregate_IAQ.csv')

    # ----------------- #
    # Hourly Data by ID #
    # ----------------- #
    
    temp = raw_data.groupby(['ID','Month','Day','Hour']).mean() # Mean for each hour for an ID
    ## Converting separate date columns to single datetime entry and writing to csv
    hourly_mean_byID = pd.Series()
    for name in id_list:
        dates = []
        df = temp.loc[name]
        for i in range(len(df)):
            dates.append(datetime(start_date.year,df.index[i][0],df.index[i][1],df.index[i][2]))
        df['Date'] = dates
        hourly_mean_byID[name] = df
        #df.to_csv('Files/' + name + '_IAQ.csv')
        
    # -------------------------- #
    # Importing Sleep Stage Data #
    # -------------------------- #

    stages_byID = pd.Series()
    # Importing and cleaning the data
    for folder in os.listdir(DIR):
        if folder[0] != '.':
            ## Important variables
            file_dir = DIR + folder + '/' # Location of file
            try:
                raw_data = pd.read_csv(file_dir + 'SleepStages.csv',header=0,names=['Time','ShortWakes','Stage_Label'],usecols=[1,3,4])
                ## Converting the time column to datetime
                raw_data['Time'] = pd.to_datetime(raw_data['Time'], format="%m/%d/%Y %I:%M:%S %p")
                raw_data = raw_data.set_index('Time') # Setting time as the dataframe index
                raw_data = raw_data.sort_index()

                # Removing data from DF that isn't in the deployment range
                start_date = datetime.strptime(starting, '%m/%d/%Y') # converting input to datetime
                end_date = datetime.strptime(ending, '%m/%d/%Y') # converting input to datetime
                ## Checking to see if there is data in the range
                if raw_data.index[-1] < start_date:
                    return df
                ## Checking to see if we are importing one day's worth of data
                elif start_date == end_date:
                    raw_data = raw_data[raw_data.index.month == start_date.month] # mask by month to ensure only one day
                    raw_data = raw_data[raw_data.index.day == start_date.day] # mask by the day
                    df = raw_data

                    # Returning dataframe with cleaned data
                    return df
                else:
                    raw_data = raw_data[start_date:end_date]
                    stages_byID[folder] = raw_data
        
            except FileNotFoundError:
                print('No sleep data file found for', folder)
                
    # Grouping Sleep Stages by hour - just to get the times, the count() doesn't matter
    stages_hourly_byID = pd.Series()
    for name in stages_byID.index:
        stages_byID[name]['Month'] = stages_byID[name].index.month
        stages_byID[name]['Day'] = stages_byID[name].index.day
        stages_byID[name]['Hour'] = stages_byID[name].index.hour
        
        df = stages_byID[name].groupby(['Month','Day','Hour']).count()
        dates = []
        for i in range(len(df)):
            dates.append(datetime(start_date.year,df.index[i][0],df.index[i][1],df.index[i][2]))
        df['Date'] = dates
        stages_hourly_byID[name] = df

    # -------------------------------- #
    # Concentration During Sleep by ID #
    # -------------------------------- #
    
    # Getting the hourly concentration profile while the user is sleeping
    sleepconcentration_hourly_byID = pd.Series()
    for name in stages_byID.index:
        if name in hourly_mean_byID.index:
            
            ## Using merge to combine the sleep times and the concentration times
            sleep_concentration = stages_hourly_byID[name].merge(hourly_mean_byID[name],left_on='Date',right_on='Date')
            sleep_concentration = sleep_concentration.set_index('Date')
            sleep_concentration = sleep_concentration.drop(['ShortWakes','Stage_Label'],axis=1)
            if len(sleep_concentration) > 5:
                sleepconcentration_hourly_byID[name] = sleep_concentration

    # Getting the median and peak concentration metrics for each night
    nightly_summary_byID = pd.Series()
    nightly_summary = pd.DataFrame()

    # ----------------------------------- #
    # Nightly Summary Aggregate and by ID #
    # ----------------------------------- #

    ## Individual data
    for name in sleepconcentration_hourly_byID.index:
        sleep_concentration = sleepconcentration_hourly_byID[name]
        times = sleepconcentration_hourly_byID[name].index
        locs = []
        for i in range(len(sleep_concentration)-1):
            if sleep_concentration.index[i+1]-sleep_concentration.index[i] > timedelta(hours = 3):
                locs.append(i+1) 
        
        concentration_byDay = np.split(sleep_concentration['AQI'],locs)
        times_byDay = np.split(times,locs)

        night = []
        peaks = []
        peak_times = []
        medians = []
        
        for i in range(len(concentration_byDay)):
            night.append(datetime.strptime(str(times_byDay[i][-1])[0:10],'%Y-%m-%d')-timedelta(days=1))
            peaks.append(max(concentration_byDay[i]))
            peak_times.append(concentration_byDay[i].idxmax())
            medians.append(concentration_byDay[i].median())

        d = {'Night': night, 'Median': medians, 'Peak': peaks, 'Peak_Time': peak_times}
        df = pd.DataFrame(data=d)
        df = df.set_index('Night')
        #df.to_csv('Files/' + name + '_SleepIAQ.csv')
        nightly_summary_byID[name] = df
        nightly_summary = pd.concat([nightly_summary,df],axis=0)
    
    ## Aggregate Data
    nightly_summary['Month'] = nightly_summary.index.month
    nightly_summary['Day'] = nightly_summary.index.day
    nightly_mean = nightly_summary.groupby(['Month','Day']).mean() # Mean for each hour
    nightly_count = nightly_summary.groupby(['Month','Day']).count() # Count for each hour
    dates = [] # list to hold dates
    ## Converting separate date columns to single datetime entry
    for i in range(len(nightly_mean)):
        dates.append(datetime(start_date.year,nightly_mean.index[i][0],nightly_mean.index[i][1]))
    nightly_mean['Date'] = dates # Attaching new column
    nightly_mean['Count'] = nightly_count['Peak']
    #nightly_mean.to_csv('Files/Aggregate_SleepIAQ.csv')
    
    return hourly_mean,daily_mean,nightly_summary,hourly_mean_byID,daily_mean_byID,sleepconcentration_hourly_byID,nightly_summary_byID

# Fitbit Sleep Stages #
# -------------------------------------------------------------- #
def importSleepStages(starting='03/11/2019', ending='04/15/2019'):
    '''
    Inputs:
        - starting: string representing the first date to use in the data range
        - ending: string representing the last date to use in the data range
    Returns a dataframe containing the timestamp and the measured variables that correspond to the file_name variable
    '''
    stages_byID = pd.Series()
    # Importing and cleaning the data
    for folder in os.listdir('Data/'):
        if folder[0] != '.':
            ## Important variables
            DIR = 'Data/' + folder + '/' # Location of file
            try:
                raw_data = pd.read_csv(DIR + 'SleepStages.csv',header=0,names=['Time','ShortWakes','Stage_Label'],usecols=[1,3,4])
                ## Converting the time column to datetime
                raw_data['Time'] = pd.to_datetime(raw_data['Time'], format="%m/%d/%Y %I:%M:%S %p")
                raw_data = raw_data.set_index('Time') # Setting time as the dataframe index
                raw_data = raw_data.sort_index()

                # Removing data from DF that isn't in the deployment range
                start_date = datetime.strptime(starting, '%m/%d/%Y') # converting input to datetime
                end_date = datetime.strptime(ending, '%m/%d/%Y') # converting input to datetime
                ## Checking to see if there is data in the range
                if raw_data.index[-1] < start_date:
                    print('\tNo data from this deployment range')
                    return df
                ## Checking to see if we are importing one day's worth of data
                elif start_date == end_date:
                    raw_data = raw_data[raw_data.index.month == start_date.month] # mask by month to ensure only one day
                    raw_data = raw_data[raw_data.index.day == start_date.day] # mask by the day

                    # Storing the cleaned data to the final dataframe
                    print('\tNumber of datapoints: ' + str(len(raw_data)))
                    df = raw_data

                    # Returning dataframe with cleaned data
                    return df
                else:
                    ## Variables to store the correct indexes
                    start_index = 0
                    end_index = -1
                    ## Looping through all values read in
                    for j in range(len(raw_data)):
                        if raw_data.index[j].month == start_date.month and raw_data.index[j].day == start_date.day:
                            ### Once we find the month and date, we want to break so that we store the first entry from that day
                            start_index = j
                            break
                        if raw_data.index[j] > start_date:
                            ### In the rare case we tried to import a day that is not present in the dataset, we have to fine the next closest
                            start_index = j
                            break

                    ## Removing the data gathered before the start index/start date
                    raw_data = raw_data[start_index:]

                    ## Looping through the remaining values
                    for j in range(len(raw_data)):
                        if raw_data.index[j] > end_date:
                            end_index = j-1
                            break
                    ## Removing the data gathered before the start index/start date
                    raw_data = raw_data[0:end_index]
                    
                    stages_byID[folder] = raw_data
        
            except FileNotFoundError:
                pass
                
    # Getting the Sleep Metrics
    sleep_metrics = pd.DataFrame()
    sleep_metrics_byID = pd.Series()
    for name in stages_byID.index:
        ## Relabeling
        sleep_stages = stages_byID[name]
        stages = sleep_stages['Stage_Label']
        times = sleep_stages.index
        
        ## Getting the different sleep times
        locs = []
        for i in range(len(sleep_stages)-1):
            # Parsing out the days by looking for timesteps greater than 5 minutes
            if sleep_stages.index[i+1]-sleep_stages.index[i] > timedelta(seconds = 300):
                locs.append(i+1)

        stages_byDay = np.split(stages,locs)
        times_byDay = np.split(times,locs)

        latency = []
        efficiency = []
        grade = []
        night = []
        time_asleep = []
        awake_percentage = []
        rem_percentage = []
        nonrem_percentage = []

        for i in range(len(stages_byDay)):
            # Checking to see if the person was in bed for at least 2 hours (120 30-second periods)
            if len(stages_byDay[i]) > 119:
                night.append(datetime.strptime(str(times_byDay[i][-1])[0:10],'%Y-%m-%d')-timedelta(days=1))
                time_asleep.append(len(stages_byDay[i])*30/60/60)
                n = 0
                while stages_byDay[i][n] == 'wake':
                    n += 1

                latency.append((n*30)/60/60)
                wake_count = 0
                rem_count = 0
                nonrem_count = 0
                for j in range(len(stages_byDay[i])):
                    if stages_byDay[i][j] == 'wake':
                        wake_count += 1
                    elif stages_byDay[i][j] == 'rem':
                        rem_count += 1
                    else:
                        nonrem_count += 1

                efficiency.append((1 - wake_count/len(stages_byDay[i]))*100)
                awake_percentage.append(wake_count/len(stages_byDay[i])*100)
                rem_percentage.append(rem_count/len(stages_byDay[i])*100)
                nonrem_percentage.append(nonrem_count/len(stages_byDay[i])*100)
                if efficiency[-1] >= 90:
                    grade.append('A')
                elif efficiency[-1] < 90 and efficiency[-1] >= 85:
                    grade.append('B')
                elif efficiency[-1] < 85 and efficiency[-1] >= 80:
                    grade.append('C')
                else:
                    grade.append('F')

        d = {'Night': night, 
             'Time_Asleep': time_asleep,
             '%Awake': awake_percentage,
             '%REM': rem_percentage,
             '%Non-REM': nonrem_percentage,
             'Latency': latency,
             'Efficiency': efficiency,
             'Efficiency_Grade': grade}
        df = pd.DataFrame(data=d)
        # Individual Data
        sleep_metrics_byID[name] = df.set_index('Night')
        sleep_metrics_byID[name].to_csv('Files/' + name + '_FitbitSQ.csv')
        # Aggregate Data
        df['ID'] = name
        sleep_metrics = pd.concat([sleep_metrics,df],axis=0,ignore_index=True)
        
    nightly_mean = sleep_metrics.groupby(['Night']).mean()
    nightly_count = sleep_metrics.groupby(['Night']).count()
    nightly_mean['Count'] = nightly_count['Time_Asleep']
    nightly_mean.to_csv('Files/Aggregate_FitbitSQ.csv')
    
    return stages_byID, sleep_metrics_byID, nightly_mean

# Biewe Sleep Surveys #
# --------------------------------------------------------------- #
def lambdaSleepSurveys(starting='03/11/2019', ending='04/15/2019'):
    '''
    Inputs:
        - starting: string representing the first date to use in the data range
        - ending: string representing the last date to use in the data range
    Returns dataframes for each individual's survey answers and the aggregate answers 
    '''
    sleep_surveys_byID = pd.Series()
    sleep_surveys = pd.DataFrame()
    # Importing and Cleaning the Data
    for folder in os.listdir('Data/'):
        if folder[0] != '.':
            DIR = 'Data/' + folder + '/beiwe_data/sleep_surveys/' # Location of file

            ## Important variables
            nights = []
            sleep_time = []
            restful_scores = []
            refresh_scores = []
            aggregate = [] # Sleep score based on summing all values
            rr = [] # Sleep score just based on refresh and restful
            normalized = [] # Sleep score that weights each survey question by the maximum value

            ## Date Range
            start_date = datetime.strptime(starting, '%m/%d/%Y') # converting input to datetime
            end_date = datetime.strptime(ending, '%m/%d/%Y') # converting input to datetime

            for file in os.listdir(DIR):
                numerics = []
                # Checking to see if the file is a csv and that date already hasn't been imported
                if file[-3:] == 'csv':
                    file_date = datetime.strptime(file[:10],'%Y-%m-%d')-timedelta(days=1)
                    # Checking to make sure we stay in the date range
                    if file_date > start_date and file_date <= end_date:
                        nights.append(file_date)
                        raw_data = pd.read_csv(DIR + file,header=None,usecols=[2,4],skiprows=1,nrows=4,names=['Question','Answer'])
                        if raw_data['Question'][0][:4] == '9:00':
                            ## Getting average number of hours slept
                            if str(raw_data['Answer'][1]).upper() == 'NAN' or raw_data['Answer'][1] == 'NOT_PRESENTED':
                                sleep_time.append(-1)
                            elif raw_data['Answer'][1] == 0:
                                sleep_time.append(0)
                            else:
                                sleep_time.append((int(raw_data['Answer'][1][0]) + int(raw_data['Answer'][1][2]))/2.0)
                            ## Getting numeric score for restfulness
                            if raw_data['Answer'][2] == 'Not at all restful':
                                restful_scores.append(0)
                            elif raw_data['Answer'][2] == 'Slightly restful':
                                restful_scores.append(1)
                            elif raw_data['Answer'][2] == 'Somewhat restful':
                                restful_scores.append(2)
                            elif raw_data['Answer'][2] == 'Very restful':
                                restful_scores.append(3)
                            else:
                                restful_scores.append(-1)
                            ## Getting numeric score for refreshedness
                            if raw_data['Answer'][3] == 'Not at all refreshed':
                                refresh_scores.append(0)
                            elif raw_data['Answer'][3] == 'Slightly refreshed':
                                refresh_scores.append(1)
                            elif raw_data['Answer'][3] == 'Somewhat refreshed':
                                refresh_scores.append(2)
                            elif raw_data['Answer'][3] == 'Very refreshed':
                                refresh_scores.append(3)
                            else:
                                refresh_scores.append(-1)
                        else:
                            sleep_time.append(int(raw_data['Answer'][0]))
                            restful_scores.append(int(raw_data['Answer'][1]))
                            refresh_scores.append(int(raw_data['Answer'][2]))
                        ## Getting Sleep Scores
                        aggregate.append(sleep_time[-1]+restful_scores[-1]+refresh_scores[-1])
                        rr.append(restful_scores[-1]+refresh_scores[-1])
                        ### Correcting for over-sleeping in the weighted score
                        temp_sleep = 0
                        if sleep_time[-1] >= 8:
                            temp_sleep = 8
                        else:
                            temp_sleep = sleep_time[-1]
                        normalized.append(restful_scores[-1]/3 + refresh_scores[-1]/3 + temp_sleep/8)

            # Sorting by day and returning
            if len(nights) > 0:
                d = {'Night': nights, 'Time_Asleep': sleep_time, 'Restful': restful_scores, 'Refreshed': refresh_scores,
                    'Aggregate': aggregate,'Refresh+Relax': rr, 'Normalized': normalized}
                df = pd.DataFrame(data=d)
                df = df.set_index('Night')
                sleep_surveys = pd.concat([sleep_surveys,df],axis=0)
                sleep_surveys_byID[folder] = df.sort_index()
                sleep_surveys_byID[folder].to_csv('Files/' + folder + '_BeiweSQ.csv')
    
    # Getting Aggregate Data
    sleep_surveys['Month'] = sleep_surveys.index.month
    sleep_surveys['Day'] = sleep_surveys.index.day
    survey_mean = sleep_surveys.groupby(['Month','Day']).mean() # Mean for each hour
    survey_count = sleep_surveys.groupby(['Month','Day']).count() # Count for each hour
    dates = [] # list to hold dates
    ## Converting separate date columns to single datetime entry
    for i in range(len(survey_mean)):
        dates.append(datetime(start_date.year,survey_mean.index[i][0],survey_mean.index[i][1]))
    survey_mean['Date'] = dates # Attaching new column
    survey_mean['Count'] = survey_count['Time_Asleep']
    survey_mean.to_csv('Files/Aggregate_BeiweSQ.csv')

    return sleep_surveys_byID, survey_mean

# ----------------- #
# Support Functions #
# ----------------- #

def getAQI(concentration):
    '''
    Input:
        - concentration: numpy float array holding the PM2.5 concentrations in ug/m^3
    Returns the PM2.5 concentration as and air quality index
    '''
    aqi = []
    for C in concentration:
        if C <= 12.0:
            aqi_score = round(C/12.0 * 50.0)
            aqi.append(aqi_score)
        elif C <= 35.4:
            aqi_score = round(50 + (C-12.1)/(35.4-12.1) * (100-50))
            aqi.append(aqi_score)
        elif C <= 55.4:
            aqi_score = round(100 + (C-35.5)/(55.4-35.5) * (150-100))
            aqi.append(aqi_score)
        elif C <= 150.4:
            aqi_score = round(150 + (C-55.5)/(150.4-55.5) * (200-150))
            aqi.append(aqi_score)
        elif C <= 250.4:
            aqi_score = round(200 + (C-150.5)/(250.4-150.5) * (300-200))
            aqi.append(aqi_score)
        elif C <= 350.4:
            aqi_score = round(300 + (C-250.5)/(350.4-250.5) * (400-300))
            aqi.append(aqi_score)
        else:
            aqi_score = round(400 + (C-350.5)/(500.4-350.5) * (500-400))
            aqi.append(aqi_score)
            
    return aqi
