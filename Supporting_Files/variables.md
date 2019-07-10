# Variables List
An overview of the variables to use for my component of the UT2000 Summer Dashboard.

## Sleep Stages

Raw data include:
- Timestamp
- Sleep Stage label (light, deep, REM, and Wake) in 30-second intervals

Derivatives include:
- Numerical descriptors for sleep stages
- Sleep efficiency calculated as percent of time NOT in the wake stage 
- Number of sustained wake periods in the night (greater than 10 minutes)

## PM Concentration

Raw data include:
- Timestamp
- PM2.5 Concentration (units?) in approximately 380 second/6.33 minute intervals
- Other concentration measures that aren't as important

Derivatives include:
- Concentration profiles during the evening when the user was asleep
- Concentration peaks during the evening when the user was asleep
- Concentration median values during the evening when the user was asleep

## Temperature and Relative Humidity

Raw data include:
- Timestamp
- Temperature values measured at 5-minute intervals
- Relative humidity measured at 5-minute intervals

Derivatives include:
- Number of times the system cycles on/off
- Time spent in ASHRAE thermal comfort zone


## Beiwe EMA Studies

Raw data include:
- Timestamp
- Perceived sleep quality questions and answers
- Various other questions and answers (not needed for this analysis)

Derivatives include:
- Perceived sleep quality score based on the answers to the sleep quality questions
