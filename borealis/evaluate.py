import json
from random import randint
from borealis import pathfinder
import numpy as np
import pandas as pd

__all__ = "evaluate"

def evaluate(board: dict) -> pd.DataFrame:
    paths = []
    changes = []

    for sq in board["board"]:
        path = pathfinder(board, sq["center"])

        if len(path) >= 5:
            paths.append(path)

            x_vals = list(range(0, len(path)))
            x = np.array(x_vals)
            y = np.empty([0, len(path)])

            air_pollution_variables = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10"]
            components = [
                [], [], [], [], [], [], []
            ]

            for index, row in path.iterrows():
                for ind, ap_v in enumerate(air_pollution_variables):
                    components[ind].append(row[ap_v])

            for c in components:
                y = np.append(y, [c], axis=0)

            change = []

            for yy in y:
                a, b = np.polyfit(x, yy, 1)
                change.append(a)
            
            changes.append(change)

    total_changes = [
        [0, 0],     # co 
        [0, 0],     # no
        [0, 0],     # no2
        [0, 0],     # o3
        [0, 0],     # so2
        [0, 0],     # pm2_5
        [0, 0],     # pm10
    ]

    for index, cc in enumerate(changes):
        for i, c in enumerate(cc):
            if c > total_changes[i][1]:
                total_changes[i][0] = index
                total_changes[i][1] = c

    # Analyze total_changes
    dups = {}
    for index, pollutant in enumerate(total_changes):
        if pollutant[0] not in dups:
            dups[pollutant[0]] = [index]
        else:
            dups[pollutant[0]].append(index)

    high: int = 0
    for item in dups:
        if len(dups[item]) > high:
            high = len(dups[item])
    maximum_indices = [key for key in dups if len(dups[key]) == high]

    if len(maximum_indices) == 1:
        return paths[maximum_indices[0]]

    elif len(maximum_indices) > 1:
        indices = {}
        pollutant_indices = []
        for key in maximum_indices:
            indices[key] = 0
            pollutant_indices += dups[key]

        inverse_pollutant_indices = [i for i in list(range(len(total_changes))) if i not in pollutant_indices]

        for idx in inverse_pollutant_indices:
            queue = []
            for max_ind in maximum_indices:
                queue.append(changes[max_ind][idx])
            
            max_in_queue = max(queue)
            max_in_queue_index = queue.index(max_in_queue)
            indices[maximum_indices[max_in_queue_index]] += 1
            del queue
        
        highest_path = [0, 0]
        for key, value in indices.items():
            if value > highest_path[1]:
                highest_path = [key, value]

        return paths[highest_path[0]]

    else:
        queue = []
        for ind in maximum_indices:
            x = list(range(len(changes[ind])))
            y = changes[ind]
            a, b = np.polyfit(x, y, 1)
            queue.append(a)
        
        max_in_queue = max(queue)
        max_in_queue_index = queue.index(max_in_queue)
        return paths[maximum_indices[max_in_queue_index]]