from datetime import datetime
from datetime import timedelta
from itertools import product
from sys import argv
from tqdm import tqdm

import json
import numpy as np
import pandas as pd

'''PART I: Setup the board JSON object'''
def create_board(prev: datetime, curr: datetime, versions: list) -> None:
    CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    # WEATHER_FILE: str = f"log/components/local_predictions_{prev.hour:02d}-{curr.hour:02d}.csv"
    # WEATHER_FILE: str = f"predictions/aurora/local_prediction_{prev.hour:02d}-{curr.hour:02d}.csv"
    WEATHER_FILE: str = f"log/components/forecast/local_predictions_{prev.hour:02d}-{curr.hour:02d}.csv"
    SAVE: str = f"log/components/forecast/board_{prev.date()}_{prev.hour:02d}00-{curr.hour:02d}00.json"
    SHIFT: float = 0.125
    PRESSURE_LEVELS: float = 13

    weather_data = pd.read_csv(WEATHER_FILE)
    weather_data['time'] = pd.to_datetime(weather_data['time'], format='ISO8601')

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

    collect_weather_and_dump(weather_data, prev, curr, PRESSURE_LEVELS, SHIFT, board)
    collect_air_pollution_and_dump(prev, curr, board, versions)

    with open(SAVE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)

'''PART II: Collect Weather -> Save to JSON object'''
def collect_weather_and_dump(df, prev, curr, pressure_levels, shift, board):
    df_cur = df[df["time"] != prev].reset_index(drop=True)
    df_old = df[df["time"] != curr].reset_index(drop=True)

    n = 13  # num of pressure levels
    
    # Splits the dataframe into even sections
    # with each piece having 13 pieces (equal to the number of pressure levels)
    list_df_cur = [df_cur[i:i + n] for i in range(0, len(df_cur), n)]
    list_df_old = [df_old[i:i + n] for i in range(0, len(df_old), n)]

    for index in range(0, len(list_df_cur)):
        old = list_df_old[index]
        cur = list_df_cur[index]

        # Find and store the relative difference between "old" data and "current" data
        board["board"][index]["weather"]["10u_wind_change"] = cur["10m_u_component_of_wind"].mean() - old["10m_u_component_of_wind"].mean()
        board["board"][index]["weather"]["10v_wind_change"] = cur["10m_v_component_of_wind"].mean() - old["10m_v_component_of_wind"].mean()
        board["board"][index]["weather"]["u_wind_change"] = cur["u_component_of_wind"].mean() - old["u_component_of_wind"].mean()
        board["board"][index]["weather"]["v_wind_change"] = cur["v_component_of_wind"].mean() - old["v_component_of_wind"].mean()
        board["board"][index]["weather"]["specific_humidity_change"] = cur["specific_humidity"].mean() - old["specific_humidity"].mean()
    
'''PART III: Collect Air Pollution -> Save to JSON object'''
# NOTE: One reason we are doing this seperatly instead of combining it with the previous function
#       is because a) it's easier to visual what each thing does and b) we have more freedom
#       to perform other functions within this one (i.e., if a quadrant does not have any data,
#       then create an API call for that quadrant's center point, get the data, and store it there.)
def collect_air_pollution_and_dump(prev, curr, board, versions):
    air_pollution_variables = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"]

    for version in versions:

        if version == "raw":
            AIR_POLLUTION_FILE: str = f"log/components/forecast/aqi_{version}_{CURRENT_TIME.date()}.csv"
            airpollution_data = pd.read_csv(AIR_POLLUTION_FILE)
            times = airpollution_data["time"].unique().tolist()
            for time in times:
                dataframe_section = airpollution_data.loc[airpollution_data.time == time].reset_index()
                for index, row in dataframe_section.iterrows():
                    for air_pollution_variable in air_pollution_variables:
                        if air_pollution_variable not in board["board"][index]["pollution"]["raw"]: board["board"][index]["pollution"][version][air_pollution_variable] = []
                        board["board"][index]["pollution"][version][air_pollution_variable].append(row[air_pollution_variable])
        else:
            AIR_POLLUTION_FILE: str = f"log/components/forecast/aqi_{version}_{prev.date()}_{prev.hour:02d}00-{curr.hour:02d}00.csv"
            airpollution_data = pd.read_csv(AIR_POLLUTION_FILE)
            for index, row in airpollution_data.iterrows(): 
                for air_pollution_variable in air_pollution_variables:
                    board["board"][index]["pollution"][version][air_pollution_variable] = row[air_pollution_variable]
    
'''PART IV: Activate all functions -> Save JSON object to JSON file'''
if __name__ == "__main__":
    CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    times = [CURRENT_TIME]
    for i in range(1, 5):
        nt = CURRENT_TIME + timedelta(hours=6*i)
        times.append(nt)

    aqi_versions = ["avg", "raw", "slr"]
    for index in range(0, 4):
        create_board(times[index], times[index+1], aqi_versions)