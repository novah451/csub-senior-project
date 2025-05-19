import math
import metpy.calc as mpcalc
from metpy.units import units
import pandas as pd
import numpy as np

__all__ = ["pathfinder"]

def pathfinder(board: dict, entry: list[float]) -> pd.DataFrame:
    """Returns a list of every point along a path based on an initial point and its weather values"""
    columns = [
        "lon", 
        "lat",
        "u_wind_change", 
        "v_wind_change", 
        "specific_humidity_change", 
        "co", 
        "no", 
        "no2", 
        "o3", 
        "so2", 
        "pm2_5", 
        "pm10", 
        # "aqi"
    ]

    recursion_counter = 0
    path: pd.DataFrame = pd.DataFrame(columns=columns)
    path = build_path(board, entry, path, recursion_counter)

    return path

def build_path(board: dict, entry: list[float, float], path: pd.DataFrame, rc: int) -> pd.DataFrame:
    delta: np.float32 = 0.25
    shift: np.float32 = 0.125
    rride: np.float32 = 0.01

    point: list[np.float32] = entry

    for i in range(0, len(board["board"])):
        if board["board"][i]["center"] == entry:
            uwind: np.float32 = board["board"][i]["weather"]["u_wind_change"]
            vwind: np.float32 = board["board"][i]["weather"]["v_wind_change"]
            spc: np.float32 = board["board"][i]["weather"]["specific_humidity_change"]
            co: np.float32 = board["board"][i]["pollution"]["slr"]["co"]
            no: np.float32 = board["board"][i]["pollution"]["slr"]["no"]
            no2: np.float32 = board["board"][i]["pollution"]["slr"]["no2"]
            o3: np.float32 = board["board"][i]["pollution"]["slr"]["o3"]
            so2: np.float32 = board["board"][i]["pollution"]["slr"]["so2"]
            pm2_5: np.float32 = board["board"][i]["pollution"]["slr"]["pm2_5"]
            pm10: np.float32 = board["board"][i]["pollution"]["slr"]["pm10"]
            # aqi: np.float32 = board["board"][i]["aqi"]
            break
    
    angle = mpcalc.wind_direction(uwind * units('m/s'), vwind * units('m/s'), 'to')
    theta: np.float32 = np.float32(angle)

    x = point[0]
    y = point[1]

    tbt: list[list[float]] = [
        [x - delta, y + delta], [x, y + delta], [x + delta, y + delta],
        [x - delta, y],         [x, y],         [x + delta, y],
        [x - delta, y - delta], [x, y - delta], [x + delta, y - delta]
    ]

    """
        The above variable can also be seen as this:
        [0] [1] [2]          |
        [3] [4] [5]     -----|-----
        [6] [7] [8]          |

    """

    if 0 <= theta <= 90:
        section: list[list[float]] = [tbt[5], tbt[2], tbt[1]]

    if 90 <= theta <= 180:
        section: list[list[float]] = [tbt[1], tbt[0], tbt[3]]

    if 180 <= theta <= 270:
        section: list[list[float]] = [tbt[3], tbt[6], tbt[7]]

    if 270 <= theta <= 360:
        section: list[list[float]] = [tbt[7], tbt[8], tbt[5]]

    # Step 1:   Update Variables
    # Step 2:   Check if outside of grid / returned to initial quadrant
    # Step 3:   Check if in new quadrant -
    #           If YES: return that point, break, and start process again
    #           If NO: return continue

    flag: str = None
    output: list[float] = None

    # BEFORE GOING TO THIS LOOP, SAVE ALL THINGS IMPORTANT TO THE PATH DATAFRAME
    # find where the last position in the path DataFrame is
    query = [
        entry[0], 
        entry[1], 
        uwind, 
        vwind, 
        spc,
        co,
        no,
        no2,
        o3,
        so2,
        pm2_5,
        pm10,
        # aqi
    ]

    # add the lon and lat from entry to the path DataFrame
    path.loc[len(path)] = query

    while True:
        x += rride * math.cos(math.radians(theta))
        y += rride * math.sin(math.radians(theta))

        for i in range(0, len(section)):
            if section[i][0] - shift <= x <= section[i][0] + shift and \
                section[i][1] - shift <= y <= section[i][1] + shift:
                # check if the section is outside the bounds of the board
                if (section[i][0] < 239.75 - shift or section[i][0] > 242.5 + shift) or \
                    (section[i][1] < 34.75 - shift or section[i][1] > 36 + shift):
                    flag = "break"
                    break
                
                # check if the section is looping:
                # if the path is like a big circle, starting a one point and never ending, then kill it
                # OR if the path has a start but a minor loop within it, then kill it
                if (section[i][0] == path["lon"][0] and section[i][1] == path["lat"][0]) or \
                    (rc > 100):
                    flag = "break"
                    break

                # if the section is valid, then prepare output
                flag = "break"
                output = [section[i][0], section[i][1]]

        if flag == "break":
            break
    
    if output:
        rc += 1
        build_path(board, output, path, rc)

    return path

if __name__ == "__main__":
    import json

    with open('../board.json', 'r') as file:
        board = json.load(file)
    
    print(pathfinder(board, board["board"][9]["center"]))
