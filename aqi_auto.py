from calendar import timegm
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from itertools import product
from requests import get
from os import getenv
from statistics import mean
from sys import argv
from tqdm import tqdm

import json
import numpy as np
import pandas as pd
import pickle

columns = ["lon", "lat", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"]
CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
times = [CURRENT_TIME]
for i in range(1, 5):
    nt = CURRENT_TIME + timedelta(hours=6*i)
    times.append(nt)

load_dotenv()
API_KEY = getenv("OPENWEATHERMAP_API_KEY")

LON = np.linspace(239.75, 242.5, 12)
LAT = np.linspace(34.75, 36, 6)
lon_by_lat: list = list(product(LAT, LON))

raw_dict = {}
averages = [{}, {}, {}, {}]
changes = [{}, {}, {}, {}]

for idx, coord in enumerate(lon_by_lat):
    # coord returns a tuple: (lat, lon). Therefore, set them to their own variables
    lat, lon = coord

    # subtract 360 because the api requires the lon to be between -180 to 180
    lon -= 360

    # -----------------------------------------------------------------------------
    # Prepare and Save each lat and lon air pollution information
    # -----------------------------------------------------------------------------
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
    response = get(url)
    response_to_json = response.json()

    components = [
        [], # holds list of "co" variables 
        [], # holds list of "no" variables
        [], # holds list of "no2" variables
        [], # holds list of "o3"" variables
        [], # holds list of "so2" variables
        [], # holds list of "pm2_5" variables
        [], # holds list of "pm10" variables
        [], # holds list of "aqi" variables
    ]

    for index in range(0, 25):
        # stores each variable per hour returned
        # example: "co" will have 25 numbers stored for each hour between [12-12]
        components[0].append(response_to_json["list"][index]["components"]["co"])
        components[1].append(response_to_json["list"][index]["components"]["no"])
        components[2].append(response_to_json["list"][index]["components"]["no2"])
        components[3].append(response_to_json["list"][index]["components"]["o3"])
        components[4].append(response_to_json["list"][index]["components"]["so2"])
        components[5].append(response_to_json["list"][index]["components"]["pm2_5"])
        components[6].append(response_to_json["list"][index]["components"]["pm10"])
        components[7].append(response_to_json["list"][index]["main"]["aqi"])

    # -----------------------------------------------------------------------------
    # Prepare and Save each hours air pollution information
    # -----------------------------------------------------------------------------
    for item_j in range(0, len(components[0])):
        query_raw_data = [
            CURRENT_TIME + timedelta(hours=item_j),
            lon+360,
            lat,
            components[0][item_j],
            components[1][item_j],
            components[2][item_j],
            components[3][item_j],
            components[4][item_j],
            components[5][item_j],
            components[6][item_j],
            components[7][item_j]
        ]
        raw_dict[len(raw_dict)] = query_raw_data

    # -----------------------------------------------------------------------------
    # Prepare and Save each 6-hours air pollution information
    # -----------------------------------------------------------------------------
    for index in range(0, 4):
        query_average_data = [
            lon+360,
            lat,
            mean(components[0][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[1][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[2][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[3][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[4][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[5][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[6][0 + (index * 6):6 + (index * 6) + 1]),
            mean(components[7][0 + (index * 6):6 + (index * 6) + 1]),
        ]
        averages[index][idx] = query_average_data

    # -----------------------------------------------------------------------------
    # Prepare and Save the SLR over 6-hours air pollution information
    # -----------------------------------------------------------------------------
    comps = np.array(components)
    for index in range(0, 4):
        x = np.array([0, 1, 2, 3, 4, 5, 6])
        y = np.empty([0, 7], float)
        pollutant_changes = []
        
        cdata = comps[:, 0 + (index * 6):6 + (index * 6) + 1]
        for c in cdata:
            y = np.append(y, [c], axis=0)

        for y_variables in y:
            # for every variable ("co", "no2", etc), find the linear regression line
            # then, keep track of the "slope" (a) value; gives us a way to numerically
            # identify the trend of the variable 
            a, b = np.polyfit(x, y_variables, 1)
            pollutant_changes.append(a)
        
        query_changes_data = [
            lon+360,
            lat,
            pollutant_changes[0],
            pollutant_changes[1],
            pollutant_changes[2],
            pollutant_changes[3],
            pollutant_changes[4],
            pollutant_changes[5],
            pollutant_changes[6],
            pollutant_changes[7],
        ]
        changes[index][idx] = query_changes_data

aqi_raw_df = pd.DataFrame.from_dict(raw_dict, orient="index", columns=["time", "lon", "lat", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"])
aqi_raw_df = aqi_raw_df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
aqi_raw_df.to_csv(f"log/components/forecast/aqi_raw_{CURRENT_TIME.date()}.csv", sep=",", index=False)

for index, average in enumerate(averages):
    aqi_average_df = pd.DataFrame.from_dict(average, orient="index", columns=columns)
    aqi_average_df.to_csv(f"log/components/forecast/aqi_avg_{times[index].date()}_{times[index].hour:02d}00-{times[index+1].hour:02d}00.csv", sep=",", index=False)

for index, change in enumerate(changes):
    aqi_changes_df = pd.DataFrame.from_dict(change, orient="index", columns=columns)
    aqi_changes_df.to_csv(f"log/components/forecast/aqi_slr_{times[index].date()}_{times[index].hour:02d}00-{times[index+1].hour:02d}00.csv", sep=",", index=False)