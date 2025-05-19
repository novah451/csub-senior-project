from datetime import date
from sys import argv

import pandas as pd
import numpy as np

CURRENT_TIME = date(int(argv[1]), int(argv[2]), int(argv[3]))

FILE = f"log/components/forecast/global_predictions_{CURRENT_TIME}.csv"
SAVE = f"log/components/forecast/local_predictions_{CURRENT_TIME}.csv"

# ONLY USE WHEN MAPPING
# FILE = f"predictions/archive/global_predictions_{CURRENT_TIME}.csv"
# SAVE = f"predictions/archive/local_predictions_{CURRENT_TIME}.csv"

# Read the CSV and convert in Dataframe
df = pd.read_csv(FILE)

# Convert the 'time' column into a 'datetime64' object type: 2024-01-02 12:00:00
df['time'] = pd.to_datetime(df['time'], format='ISO8601')

'''PART II: Filter Data for Only Kern County'''
# Base filter on rang of lon and lat: Lon = range(239.75, 242.5), Lat = range(34.75, 36)
df = df[(df['lat'] >= 34.75) & (df['lat'] <= 36) & (df['lon'] >= 239.75) & (df['lon'] <= 242.5)]

# ONLY USE WHEN MAPPING
# "area": [37, 239.25, 34, 243],
# df = df[(df['lat'] >= 34) & (df['lat'] <= 37) & (df['lon'] >= 239.25) & (df['lon'] <= 243)]

'''PART III: Save Dataframe to CSV'''
# Save new dataframe as CSV
df = df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
df.to_csv(SAVE, na_rep='null', index=False)