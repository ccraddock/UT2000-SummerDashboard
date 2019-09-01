

def lambdaThermalConditions(starting='03/11/2019', ending='04/15/2019'):
    '''
    Inputs:
        - starting: string representing the first date to use in the data range
        - ending: string representing the last date to use in the data range
        - Might want to include a DIR input for where the data are stored
    Returns two dataframes and two series of dataframes:
        - df of averaged values for temperature and relative humidity across all users by HOUR
        - df of averaged values for temperature and relative humdidity across all users by DAY
        - series with dataframes for each individual with data at each HOUR
        - series with dataframes for each individual with data at each DAY

    '''
    raw_data = pd.DataFrame() # Stores all data
    id_list = []
    # Hagen's local directory
    DIR = "/~/Google\ Drive/Research/5_Sensors/Projects/UT2000-SummerDashboard/Code_Development/Data/"

    # Importing the data
    for folder in os.listdir(DIR):
        ## Checking for any hidden files 
        if folder[0] != '.':
            id_list.append(folder) # Adding the ID to the list
            temp = pd.DataFrame() # Stores one csv file's worth of data

            ## Looping through all the files in the sensor directory
            for file in os.listdir(DIR+folder):
                if str(file[-3:]) == 'csv': # To ensure that we only read in csv files
                    temp = pd.read_csv(DIR + file,header=None,names=['Time','Relative Humidity','Temperature(C)'])
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
    daily_mean.to_csv('Files/Aggregate_ThermalConditions_Daily.csv')

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
        df.to_csv('Files/' + name + '_ThermalConditions_Hourly.csv')
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
    hourly_mean.to_csv('Files/Aggregate_ThermalConditions_Hourly.csv')

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
        df.to_csv('Files/' + name + '_ThermalConditions_Hourly.csv')
        hourly_mean_byID[name] = df


    return hourly_mean,hourly_mean_byID,daily_mean,daily_mean_byID
