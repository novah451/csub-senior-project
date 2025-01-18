# setup this file so that the user can just choose which one they want to run
# 1. Ask the user which model they want to run
# 2. Run the model.
# 3. Run the filter script.
# 4. Run the board script.
# 5. Profit
from borealis import aqi
from borealis import create_board
from borealis import evaluate
from dotenv import load_dotenv

import os
import json

load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

with open('board.json', 'r') as file:
    board = json.load(file)

'''COMMENT THESE TWO OUT IF YOU ALREADY HAVE THEM
DON'T WASTE API CALLS WHEN RUNNING aqi()'''
# aqi(API_KEY)
# create_board()

# returns the path as a DataFrame; change as you wish
origin_path = evaluate(board)
origin = [origin_path.iloc[0]["lon"], origin_path.iloc[0]["lat"]]

print("Path from Origin: \n")
print(origin_path)
print("Origin Square:", origin, "\n")
