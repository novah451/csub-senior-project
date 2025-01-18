from datetime import datetime
from datetime import timedelta
from sys import argv

import numpy as np
import pandas as pd

"""PREREQUISITES / CONSTANTS"""
# Specific dates to port over
CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
PREVIOUS_TIME = CURRENT_TIME - timedelta(hours=6)

print(PREVIOUS_TIME, CURRENT_TIME)

# File Path(s)
pt_5minBefore = PREVIOUS_TIME - timedelta(minutes=5)
FILE = f"predictions/aurora/local_predictions_{pt_5minBefore.date()}.csv"
SAVE = f"log/components/local_predictions_{PREVIOUS_TIME.hour:02d}-{CURRENT_TIME.hour:02d}.csv"

print(SAVE)

print("Accessing:", FILE)
print("Saving to:", SAVE)

if CURRENT_TIME.hour != 12:
    # Read the CSV and convert in Dataframe
    df = pd.read_csv(FILE)

    # Convert the 'time' column into a 'datetime64' object type: 2024-01-02 12:00:00
    df['time'] = pd.to_datetime(df['time'], format='ISO8601')

    '''PART II: Filter Data for Only Kern County ==> CHANGE THIS PART TO BE A SEPERATE FILE
    THIS IS SO THAT WE DON'T HAVE TO CONTINOUSLY OPEN A LARGE FILE AND FILTER IT OUT:

    EXAMPLE - TIME IS 12:00 PM
        1. global_predictions_2024-01-15.csv
        2. local_predictions_2024-01-15.csv
        3. local_predictions_6-12.csv'''
    
    # Base filter on rang of lon and lat: Lon = range(239.75, 242.5), Lat = range(34.75, 36)
    # df = df[(df['lat'] >= 34.75) & (df['lat'] <= 36) & (df['lon'] >= 239.75) & (df['lon'] <= 242.5)]

    '''PART III: FIlter Data for Only 12:00 - 18:00'''
    # Base filter on range of time: range(12:00, 18:00)
    df = df[(df['time'] >= PREVIOUS_TIME) & (df['time'] <= CURRENT_TIME)]

    '''PART IV: Save Dataframe to CSV'''
    # Save new dataframe as CSV
    df = df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
    df.to_csv(SAVE, na_rep='null', index=False)
else:
    day_old_file = CURRENT_TIME - timedelta(days=1)
    OLD_FILE = f"predictions/aurora/local_predictions_{day_old_file.date()}.csv"

    print("OLD FILE:", OLD_FILE)
    print("FOO TIME:", PREVIOUS_TIME)

    exit(0)

    df_now = pd.read_csv(FILE)
    df_old = pd.read_csv(OLD_FILE)

    df_now['time'] = pd.to_datetime(df_now['time'], format='ISO8601')
    df_old['time'] = pd.to_datetime(df_old['time'], format='ISO8601')
    
    df_now = df_now[(df_now['time'] == CURRENT_TIME)]
    df_old = df_old[(df_old['time'] == PREVIOUS_TIME)]

    frames = [df_old, df_now]
    df = pd.concat(frames)

    df = df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
    df.to_csv(SAVE, na_rep='null', index=False)
