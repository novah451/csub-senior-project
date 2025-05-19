from datetime import datetime
from datetime import timedelta
from itertools import product
from metpy.calc import wind_components
from metpy.units import units
from sys import argv
from tqdm import tqdm

import json
import numpy as np
import pandas as pd

'''PART I: Setup the board JSON object'''
def create_board(prev: datetime, curr: datetime, versions: list) -> None:
    WEATHER_FILE: str = f"log/components/current/local_weather_{prev.hour:02d}00-{curr.hour:02d}00.csv"
    SAVE: str = f"log/components/current/board_{prev.date()}_{prev.hour:02d}00-{curr.hour:02d}00.json"
    SHIFT: float = 0.125

    weather_data = pd.read_csv(WEATHER_FILE)

    lon = weather_data["lon"].unique()
    lat = weather_data["lat"].unique()
    lon_by_lat: list = list(product(lat, lon))

    board = {
        "time": {
            "previous": {
                "year": str(prev.year),
                "month": f"{prev.month:02d}",
                "day": f"{prev.day:02d}",
                "hour": f"{prev.hour:02d}",
                "minute": f"{prev.minute:02d}",
            },
            "current": {
                "year": str(curr.year),
                "month": f"{curr.month:02d}",
                "day": f"{curr.day:02d}",
                "hour": f"{curr.hour:02d}",
                "minute": f"{curr.minute:02d}",
            }
        },
        "board": []
    }

    """
    [x - delta, y + delta], [x, y + delta], [x + delta, y + delta],
    [x - delta, y],         [x, y],         [x + delta, y],
    [x - delta, y - delta], [x, y - delta], [x + delta, y - delta]
    """

    for coord in lon_by_lat:
        center = [coord[1], coord[0]]
        query = {
            "center": center,
            "vertices": [            # When saving it goes TOP LEFT, TOP RIGHT, BOTTOM LEFT, BOTTOM RIGHT
                (center[0] - SHIFT, center[1] + SHIFT), 
                (center[0] + SHIFT, center[1] + SHIFT), 
                (center[0] - SHIFT, center[1] - SHIFT), 
                (center[0] + SHIFT, center[1] - SHIFT)
            ],
            "weather": {},
            "pollution": {
                "avg": {},
                "raw": {},
                "slr": {}
            },
        }
        board["board"].append(query)

    collect_weather_and_dump(weather_data, prev, curr, board)
    collect_air_pollution_and_dump(prev, curr, board, versions)

    with open(SAVE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)

'''PART II: Collect Weather -> Save to JSON object'''
def collect_weather_and_dump(df, prev, curr, board):
    for index in range(0, len(df)):
        wind_speed = df.loc[[index]]["wind_speed_mean"].values[0]
        degrees = df.loc[[index]]["wind_degrees_mean"].values[0]
        u, v = wind_components(wind_speed * units('m/s'), degrees * units.deg)

        # Find and store the relative difference between "old" data and "current" data
        board["board"][index]["weather"]["u_wind_change"] = u.magnitude
        board["board"][index]["weather"]["v_wind_change"] = v.magnitude
        board["board"][index]["weather"]["specific_humidity_change"] = df.loc[[index]]["humidity_mean"].values[0]
    
'''PART III: Collect Air Pollution -> Save to JSON object'''
# NOTE: One reason we are doing this seperatly instead of combining it with the previous function
#       is because a) it's easier to visual what each thing does and b) we have more freedom
#       to perform other functions within this one (i.e., if a quadrant does not have any data,
#       then create an API call for that quadrant's center point, get the data, and store it there.)
def collect_air_pollution_and_dump(prev, curr, board, versions):
    air_pollution_variables = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"]

    for version in versions:
        AIR_POLLUTION_FILE: str = f"log/components/current/aqi_{version}_{curr.year:02d}_{curr.month:02d}_{(curr - timedelta(minutes=5)).day:02d}_{prev.hour:02d}00-{curr.hour:02d}00.csv"
        airpollution_data = pd.read_csv(AIR_POLLUTION_FILE)

        if version == "raw":
            times = airpollution_data["time"].unique().tolist()
            for time in times:
                dataframe_section = airpollution_data.loc[airpollution_data.time == time].reset_index()
                for index, row in dataframe_section.iterrows():
                    for air_pollution_variable in air_pollution_variables:
                        if air_pollution_variable not in board["board"][index]["pollution"]["raw"]: board["board"][index]["pollution"][version][air_pollution_variable] = []
                        board["board"][index]["pollution"][version][air_pollution_variable].append(row[air_pollution_variable])
        else:
            for index, row in airpollution_data.iterrows(): 
                for air_pollution_variable in air_pollution_variables:
                    board["board"][index]["pollution"][version][air_pollution_variable] = row[air_pollution_variable]
    
'''PART IV: Activate all functions -> Save JSON object to JSON file'''
if __name__ == "__main__":
    CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    PREVIOUS_TIME = CURRENT_TIME - timedelta(hours=6)

    aqi_versions = ["avg", "raw", "slr"]
    create_board(PREVIOUS_TIME, CURRENT_TIME, aqi_versions)