from datetime import datetime
from datetime import timedelta
from sys import argv
import json
import pandas as pd

def create_board(prev: datetime = None, curr: datetime = None) -> None:
    '''PREREQUISITES: CONSTANTS'''
    WEATHER_FILE: str = f"predictions/aurora/local_predictions_{prev.hour}-{curr.hour}.csv"
    AIR_POLLUTION_FILE: str = "aqi.csv"
    SAVE: str = f"board_{prev.hour}-{curr.hour}.json"
    SHIFT: float = 0.125
    PRESSURE_LEVELS: float = 13

    if prev is None and curr is None:
        prev: datetime = datetime(2024, 11, 1, 12, 0, 0)
        curr: datetime = datetime(2024, 11, 1, 18, 0, 0)

    df: pd.DataFrame = pd.read_csv(WEATHER_FILE)
    ap_df: pd.DataFrame = pd.read_csv(AIR_POLLUTION_FILE)

    df['time'] = pd.to_datetime(df['time'], format='ISO8601')

    # TODO: check if board.json exists -> if yes, set this var to it
    board = {"board": []}

    LON = df["lon"].unique()
    LAT = df["lat"].unique()

    board_setup(LAT, LON, board)
    collect_weather_and_dump(df, prev, curr, PRESSURE_LEVELS, SHIFT, board)
    collect_air_pollution_and_dump(ap_df, board)

    with open(SAVE, 'w', encoding='utf-8') as f:
        json.dump(board, f, ensure_ascii=False, indent=4)


'''PART I: Setup the board JSON object'''
def board_setup(lat, lon, board):
    TMP = []
    GRD = []
    LAT_FLG = ""

    for y in range(len(lat)):
        if y > 0:
            LAT_FLG = "PAIR"
        for x in range(len(lon)):
            val = (float(lon[x]), float(lat[y]))
            TMP.append(val)

            if x > 0 and LAT_FLG == "PAIR":
                END = len(TMP) - 1
                query = [TMP[0], TMP[1], TMP[END-1], TMP[END]]
                GRD.append(query)
                TMP.pop(0)

            if x == len(lon) - 1 and LAT_FLG == "PAIR":
                TMP.pop(0)

    for square in GRD:
        X = (square[0][0] + square[3][0]) / 2
        Y = (square[0][1] + square[3][1]) / 2
        center = [X, Y]

        query = {"center": center}
        board["board"].append(query)

'''PART II: Collect Weather -> Save to JSON object'''
def collect_weather_and_dump(df, prev, curr, pressure_levels, shift, board):
    # original_wv = ["10m_u_component_of_wind", "10m_v_component_of_wind", "specific_humidity", "total_precipitation_6hr"]
    original_wv = ["u_component_of_wind", "v_component_of_wind", "specific_humidity"]

    # weather_variables = ["u_wind_change", "v_wind_change", "specific_humidity_change", "tot_precipitation_change"]
    weather_variables = ["u_wind_change", "v_wind_change", "specific_humidity_change"]
    col = ["lon", "lat"]
    col.extend(weather_variables)
    board_df = pd.DataFrame(columns=col)

    df_cur = df[df["time"] != prev].reset_index(drop=True)
    df_old = df[df["time"] != curr].reset_index(drop=True)

    endpoint = df_cur["lon"].nunique() * df_cur["lat"].nunique()
    mul = 1

    # both dataframes are same length, won't matter which is chosen
    for _ in range(0,endpoint):
        ind = pressure_levels * mul

        x = df_cur.iloc[ind-pressure_levels:ind]
        y = df_old.iloc[ind-pressure_levels:ind]

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

            if (x_coord - shift <= lon <= x_coord + shift) and (y_coord - shift <= lat <= y_coord + shift):
                for ind, p in enumerate(weather_variables):
                    board["board"][index][p] = float(wv[ind])

'''PART III: Collect Air Pollution -> Save to JSON object'''
# NOTE: One reason we are doing this seperatly instead of combining it with the previous function
#       is because a) it's easier to visual what each thing does and b) we have more freedom
#       to perform other functions within this one (i.e., if a quadrant does not have any data,
#       then create an API call for that quadrant's center point, get the data, and store it there.)
def collect_air_pollution_and_dump(ap_df, board):
    air_pollution_variables = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10"]

    # First Pass of Board -> Set the inital points in
    for index, row in ap_df.iterrows(): 
        for ap_v in air_pollution_variables:
            board["board"][index][ap_v] = row[ap_v]
    
'''PART IV: Activate all functions -> Save JSON object to JSON file'''
if __name__ == "__main__":
    CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)
    PREVIOUS_TIME = CURRENT_TIME - timedelta(hours=6)

    create_board(PREVIOUS_TIME, CURRENT_TIME)
