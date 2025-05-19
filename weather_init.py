from calendar import timegm
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from itertools import product
from requests import get
from os import getenv
from statistics import mean
from sys import argv

import json
import numpy as np
import pandas as pd
import pickle

def weather(time: datetime, mode: str='collect'):
    load_dotenv()
    API_KEY = getenv("OPENWEATHERMAP_API_KEY")

    LON = np.linspace(239.75, 242.5, 12)
    LAT = np.linspace(34.75, 36, 6)
    lon_by_lat = list(product(LAT, LON))

    collection = {}
    for idx, coord in enumerate(lon_by_lat):
        # coord returns a tuple: (lat, lon). Therefore, set them to their own variables
        lat, lon = coord
        # subtract 360 because the api requires the lon to be between -180 to 180
        lon -= 360

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
        response = get(url)
        response_to_json = response.json()

        query = [
            time,
            lon + 360,
            lat,
            response_to_json["main"]["temp"],
            response_to_json["main"]["humidity"],
            response_to_json["wind"]["speed"],
            response_to_json["wind"]["deg"],
        ]
        collection[idx] = query
    
    weather_df = pd.DataFrame.from_dict(collection, orient="index", columns=["time", "lon", "lat", "temperature", "humidity", "wind_speed", "wind_degrees"])
    weather_df = weather_df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
    weather_df.to_csv(f"log/components/current/weather_{time.hour:02d}00.csv", sep=",", index=False)

    if mode == "dump":
        ultima = {}
        ultima_dfs = []

        if time.hour + 1 == 1:
            # Edge case for whenever it is midnight
            hours = list(range((time-timedelta(hours=5)).hour, 24))
            hours.append(0)
        else:
            # For literally any other hour (the midnight edgecase is SO ANNOYING)
            hours = list(range((time-timedelta(hours=5)).hour, time.hour + 1))

        for hour in hours:
            df = pd.read_csv(f"log/components/current/weather_{hour:02d}00.csv")
            ultima_dfs.append(df)
        
        for idx in range(0, len(ultima_dfs[0])):
            variables = [[], [], [], []]

            for jdx in ultima_dfs:
                variables[0].append(jdx.iloc[[idx]]['temperature'].astype(float).values[0])
                variables[1].append(jdx.iloc[[idx]]['humidity'].astype(float).values[0])
                variables[2].append(jdx.iloc[[idx]]['wind_speed'].astype(float).values[0])
                variables[3].append(jdx.iloc[[idx]]['wind_degrees'].astype(float).values[0])

            query = [
                ultima_dfs[0].iloc[[idx]]['lon'].values[0],
                ultima_dfs[0].iloc[[idx]]['lat'].values[0],
                mean(variables[0]),
                mean(variables[1]),
                mean(variables[2]),
                mean(variables[3])
            ]
            ultima[idx] = query
        
        dump_weather_df = pd.DataFrame.from_dict(ultima, orient="index", columns=["lon", "lat", "temperature_mean", "humidity_mean", "wind_speed_mean", "wind_degrees_mean"])
        dump_weather_df = dump_weather_df.sort_values(by=["lat", "lon"], ascending=[True, True])
        dump_weather_df.to_csv(f"log/components/current/local_weather_{(time-timedelta(hours=6)).hour:02d}00-{time.hour:02d}00.csv", sep=",", index=False)


if __name__ == "__main__":
    timesig = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)

    from metpy.calc import wind_components
    from metpy.units import units

    wind_speed = 10
    degrees = 225
    u, v = wind_components(wind_speed * units('m/s'), degrees * units.deg)

    print(u.magnitude, v.magnitude)

    if argv[5] != "dump": weather(timesig)
    else: weather(timesig, 'dump')

