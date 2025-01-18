from calendar import timegm
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from itertools import product
from requests import get
from os import getenv
from sys import argv

import numpy as np
import pandas as pd

def aqi(api_key: str, prev: datetime = None, curr: datetime = None) -> None:
    columns = ["lon", "lat", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10"]

    if prev is None and curr is None:
        prev = datetime(2024, 11, 1, 12, 0, 0)
        curr = datetime(2024, 11, 1, 18, 0, 0)

    start = timegm(prev.timetuple())
    end = timegm(curr.timetuple())

    LON = np.arange(239.875, 242.625, 0.25)     # RANGE OF 239.75 to 242.50
    LAT = np.arange(34.875, 36, 0.25)           # RANGE OF 34.75 to 36
    lon_by_lat: list = list(product(LAT, LON))

    query_dict = {}

    for index, coord in enumerate(lon_by_lat):
        lat, lon = coord
        lon -= 360

        url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={api_key}"
        response = get(url)
        response_to_json = response.json()

        x = np.array([0, 1, 2, 3, 4, 5, 6])
        y = np.empty([0, 7], float)

        components = [
            [], [], [], [], [], [], []
        ]

        for info in response_to_json["list"]:
            components[0].append(info["components"]["co"])
            components[1].append(info["components"]["no"])
            components[2].append(info["components"]["no2"])
            components[3].append(info["components"]["o3"])
            components[4].append(info["components"]["so2"])
            components[5].append(info["components"]["pm2_5"])
            components[6].append(info["components"]["pm10"])
        
        for c in components:
            y = np.append(y, [c], axis=0)

        changes = []

        for yy in y:
            a, b = np.polyfit(x, yy, 1)
            changes.append(a)

        query_data = [
            lon + 360,
            lat,
            changes[0],
            changes[1],
            changes[2],
            changes[3],
            changes[4],
            changes[5],
            changes[6],
        ]

        query_dict[index] = query_data

    aqi_df = pd.DataFrame.from_dict(query_dict, orient="index", columns=columns)
    aqi_df.to_csv("aqi.csv", sep=",", index=False)

if __name__ == "__main__":
    load_dotenv()
    API_KEY = getenv("OPENWEATHERMAP_API_KEY")

    curr = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    prev = curr - timedelta(hours=6)

    print(curr, prev)
    aqi(API_KEY, prev, curr)

