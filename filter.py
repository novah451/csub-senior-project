from datetime import datetime
import numpy as np
import pandas as pd

"""PREREQUISITES / CONSTANTS"""
# File Path(s)
FILE = "predictions/aurora/predictions.csv"
SAVE = "predictions/aurora/predictions_12-18.csv"

# Specific dates to port over -> Currently does 00:00 and 06:00
TIME_1 = datetime(2023, 1, 1, 12, 0, 0)
TIME_2 = datetime(2023, 1, 1, 18, 0, 0)

# Read the CSV and convert in Dataframe
df = pd.read_csv(FILE)

# Create New Dataframe -> Will be saved as CSV file

# Convert the 'time' column into a 'datetime64' object type: 2024-01-02 06:00:00
df['time'] = pd.to_datetime(df['time'], format='ISO8601')

'''PART II: Filter Data for Only Kern County'''
# Base filter on rang of lon and lat: Lon = range(239, 242), Lat = range(34, 36)
df = df[(df['lat'] >= 34) & (df['lat'] <= 36) & (df['lon'] >= 239) & (df['lon'] <= 242)]

'''PART III: FIlter Data for Only 00:00 - 06:00'''
# Base filter on range of time: range(00:00, 06:00)
df = df[(df['time'] >= TIME_1) & (df['time'] <= TIME_2)]

'''PART IV: Save Dataframe to CSV'''
# Save new dataframe as CSV
df = df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
df.to_csv(SAVE, na_rep='null', index=False)