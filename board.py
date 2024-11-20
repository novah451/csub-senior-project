from datetime import datetime
from dotenv import load_dotenv
import json
import numpy as np
import os
import pandas as pd
from requests import get
import statistics as st
from sys import argv

'''PREREQUISITES: CONSTANTS'''
WEATHER_FILE: str = "predictions/aurora/predictions_12-18.csv"
AIR_POLLUTION_FILE: str = "kern_county_aqi.csv"
SAVE: str = "board.json"
SHIFT: float = 0.125
PRESSURE_LEVELS: float = 13

TIME_1: datetime = datetime(2024, 11, 1, 12, 0, 0)
TIME_2: datetime = datetime(2024, 11, 1, 18, 0, 0)

load_dotenv()
API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY")

df: pd.DataFrame = pd.read_csv(WEATHER_FILE)
ap_df: pd.DataFrame = pd.read_csv(AIR_POLLUTION_FILE)

df['time'] = pd.to_datetime(df['time'], format='ISO8601')

# TODO: check if board.json exists -> if yes, set this var to it
board = {"board": []}

LON = df["lon"].unique()
LAT = df["lat"].unique()

'''PREREQUISITES: FUNCTIONS'''
def air_pollution_api(lat, lon):
    # Build out API Call URL
    url: str = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    # Call API
    response = get(url)
    # Parse the response
    response_to_json = response.json()
    return response_to_json

'''PART I: Setup the board JSON object'''
def board_setup():
    TMP = []
    GRD = []
    LAT_FLG = ""

    for y in range(len(LAT)):
        if y > 0:
            LAT_FLG = "PAIR"
        for x in range(len(LON)):
            val = (float(LON[x]), float(LAT[y]))
            TMP.append(val)

            if x > 0 and LAT_FLG == "PAIR":
                END = len(TMP) - 1
                query = [TMP[0], TMP[1], TMP[END-1], TMP[END]]
                GRD.append(query)
                TMP.pop(0)

            if x == len(LON) - 1 and LAT_FLG == "PAIR":
                TMP.pop(0)

    for square in GRD:
        X = (square[0][0] + square[3][0]) / 2
        Y = (square[0][1] + square[3][1]) / 2
        center = [X, Y]

        query = {"center": center}
        board["board"].append(query)

'''PART II: Collect Weather -> Save to JSON object'''
def collect_weather_and_dump():
    # original_wv = ["10m_u_component_of_wind", "10m_v_component_of_wind", "specific_humidity", "total_precipitation_6hr"]
    original_wv = ["u_component_of_wind", "v_component_of_wind", "specific_humidity"]

    # weather_variables = ["u_wind_change", "v_wind_change", "specific_humidity_change", "tot_precipitation_change"]
    weather_variables = ["u_wind_change", "v_wind_change", "specific_humidity_change"]
    col = ["lon", "lat"]
    col.extend(weather_variables)
    board_df = pd.DataFrame(columns=col)

    df_cur = df[df["time"] != TIME_1].reset_index(drop=True)
    df_old = df[df["time"] != TIME_2].reset_index(drop=True)

    endpoint = df_cur["lon"].nunique() * df_cur["lat"].nunique()
    mul = 1

    # both dataframes are same length, won't matter which is chosen
    for _ in range(0,endpoint):
        ind = PRESSURE_LEVELS * mul
        # ind = PRESSURE_LEVELS * mul

        x = df_cur.iloc[ind-PRESSURE_LEVELS:ind]
        y = df_old.iloc[ind-PRESSURE_LEVELS:ind]

        query = {
            "lon": x["lon"].iloc[0],
            "lat": x["lat"].iloc[0],
        }

        for index, key in enumerate(original_wv):
            mean_x = x[key].mean()
            mean_y = y[key].mean()
            query[weather_variables[index]] = mean_y - mean_x

        query_df = pd.DataFrame([query])
        board_df = pd.concat([board_df, query_df], ignore_index=True)

        mul += 1

    # Going through dataframe and inserting into appropriate spot in json    
    for i in range(0, len(board_df)):
        lon = board_df.loc[i, "lon"]
        lat = board_df.loc[i, "lat"]

        wv = []
        for k in weather_variables:
            wv.append(board_df.loc[i, k])

        for index, j in enumerate(board["board"]):
            x_coord = j["center"][0]
            y_coord = j["center"][1]

            if (x_coord - SHIFT <= lon <= x_coord + SHIFT) and (y_coord - SHIFT <= lat <= y_coord + SHIFT):
                for ind, p in enumerate(weather_variables):
                    board["board"][index][p] = float(wv[ind])

'''PART III: Collect Air Pollution -> Save to JSON object'''
# NOTE: One reason we are doing this seperatly instead of combining it with the previous function
#       is because a) it's easier to visual what each thing does and b) we have more freedom
#       to perform other functions within this one (i.e., if a quadrant does not have any data,
#       then create an API call for that quadrant's center point, get the data, and store it there.)
def collect_air_pollution_and_dump():
    air_pollution_variables = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "aqi"]

    # First Pass of Board -> Set the inital points in
    for index, row in ap_df.iterrows(): 
        lat = row["latitude"]
        lon = row["longitude"] + 360

        for ind, sq in enumerate(board["board"]):
            x_coord = sq["center"][0]
            y_coord = sq["center"][1]

            if "aqi" in board["board"][ind]:
                # print(f"There's already data at {ind}, skipping")
                for wv in air_pollution_variables:
                    board["board"][ind][wv] = (board["board"][ind][wv] + row[wv]) / 2
            else:
                if (x_coord - SHIFT <= lon <= x_coord + SHIFT) and (y_coord - SHIFT <= lat <= y_coord + SHIFT):
                    # print("yessir")
                    for j, var in enumerate(air_pollution_variables):
                        board["board"][ind][var] = row[var]
    
    # Second Pass of Board -> Set points in if there are none
    for ind, sq in enumerate(board["board"]):
        x_coord = sq["center"][0]
        y_coord = sq["center"][1]

        if "aqi" not in board["board"][ind]:
            # print("not here")
            data = air_pollution_api(y_coord, x_coord - 360)
            aqi = data["list"][0]["main"]
            pol = data["list"][0]["components"]
            for wv in air_pollution_variables:
                if wv == "aqi":
                    board["board"][ind][wv] = aqi[wv]
                else:
                    board["board"][ind][wv] = pol[wv]


'''PART IV: Activate all functions -> Save JSON object to JSON file'''
if __name__ == "__main__":
    board_setup()
    collect_weather_and_dump()
    collect_air_pollution_and_dump()

    with open(SAVE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)
