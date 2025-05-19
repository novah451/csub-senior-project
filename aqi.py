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

def aqi(api_key: str, prev: datetime = None, curr: datetime = None) -> None:
    columns = ["lon", "lat", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"]

    if prev is None and curr is None:
        prev = datetime(2024, 11, 1, 12, 0, 0)
        curr = datetime(2024, 11, 1, 18, 0, 0)

    start = timegm(prev.timetuple())
    end = timegm(curr.timetuple())

    # LON = np.arange(239.875, 242.625, 0.25)     # RANGE OF 239.75 to 242.50
    # LAT = np.arange(34.875, 36, 0.25)           # RANGE OF 34.75 to 36
    LON = np.linspace(239.75, 242.5, 12)
    LAT = np.linspace(34.75, 36, 6)
    lon_by_lat: list = list(product(LAT, LON))

    raw_dict = {}
    average_dict = {}
    changes_dict = {}

    for index, coord in enumerate(tqdm(lon_by_lat)):
        # coord returns a tuple: (lat, lon). Therefore, set them to their own variables
        lat, lon = coord
        # subtract 360 because the api requires the lon to be between -180 to 180
        lon -= 360

        url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={api_key}"
        response = get(url)
        response_to_json = response.json()

        x = np.array([0, 1, 2, 3, 4, 5, 6])
        y = np.empty([0, 7], float)

        components = [
            [], # holds list of "co" variables 
            [], # holds list of "no" variables
            [], # holds list of "no2" variables
            [], # holds list of "o3"" variables
            [], # holds list of "so2" variables
            [], # holds list of "pm2_5" variables
            [], # holds list of "pm10" variables
            []  # holds list of "aqi" variables
        ]

        for i, info in enumerate(response_to_json["list"]):
            # stores each variable per hour returned
            # example: "co" will have 6 numbers stored if the interval is 6-hours
            components[0].append(info["components"]["co"])
            components[1].append(info["components"]["no"])
            components[2].append(info["components"]["no2"])
            components[3].append(info["components"]["o3"])
            components[4].append(info["components"]["so2"])
            components[5].append(info["components"]["pm2_5"])
            components[6].append(info["components"]["pm10"])
            components[7].append(info["main"]["aqi"])
        
        for item_j in range(0, len(components[0])):
            query_raw_data = [
                prev + timedelta(hours=item_j),
                lon + 360,
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

        for c in components:
            y = np.append(y, [c], axis=0)

        pollutant_changes = []

        for y_variables in y:
            # for every variable ("co", "no2", etc), find the linear regression line
            # then, keep track of the "slope" (a) value; gives us a way to numerically
            # identify the trend of the variable 
            a, b = np.polyfit(x, y_variables, 1)
            pollutant_changes.append(a)

        query_average_data = [
            lon + 360,
            lat,
            mean(components[0]),
            mean(components[1]),
            mean(components[2]),
            mean(components[3]),
            mean(components[4]),
            mean(components[5]),
            mean(components[6]),
            mean(components[7])
        ]
        average_dict[index] = query_average_data

        query_changes_data = [
            lon + 360,
            lat,
            pollutant_changes[0],
            pollutant_changes[1],
            pollutant_changes[2],
            pollutant_changes[3],
            pollutant_changes[4],
            pollutant_changes[5],
            pollutant_changes[6],
            pollutant_changes[7]
        ]
        changes_dict[index] = query_changes_data

    aqi_raw_df = pd.DataFrame.from_dict(raw_dict, orient="index", columns=["time", "lon", "lat", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"])
    aqi_raw_df = aqi_raw_df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
    aqi_raw_df.to_csv(f"log/components/current/aqi_raw_{curr.year:02d}_{curr.month:02d}_{(curr - timedelta(minutes=5)).day:02d}_{prev.hour:02d}00-{curr.hour:02d}00.csv", sep=",", index=False)

    aqi_average_df = pd.DataFrame.from_dict(average_dict, orient="index", columns=columns)
    aqi_average_df.to_csv(f"log/components/current/aqi_avg_{curr.year:02d}_{curr.month:02d}_{(curr - timedelta(minutes=5)).day:02d}_{prev.hour:02d}00-{curr.hour:02d}00.csv", sep=",", index=False)

    aqi_changes_df = pd.DataFrame.from_dict(changes_dict, orient="index", columns=columns)
    aqi_changes_df.to_csv(f"log/components/current/aqi_slr_{curr.year:02d}_{curr.month:02d}_{(curr - timedelta(minutes=5)).day:02d}_{prev.hour:02d}00-{curr.hour:02d}00.csv", sep=",", index=False)


if __name__ == "__main__":
    load_dotenv()
    API_KEY = getenv("OPENWEATHERMAP_API_KEY")

    curr = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    prev = curr - timedelta(hours=6)

    print(curr, prev)
    aqi(API_KEY, prev, curr)

