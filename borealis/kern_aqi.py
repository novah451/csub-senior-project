from dotenv import load_dotenv
import os
import pandas as pd
from requests import get

'''PREREQUISITES | CONSTANTS'''
# Name of CSV file
FILE = "kern_county_aqi.csv"

# Load enviroment variables | Get API Key for later use
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Load csv file
df = pd.read_csv(FILE)

'''PART I: Get the Pollutant Concentrations & AQI'''
# Iterate through each row in Dataframe
for index, row in df.iterrows():   
    # Build out API Call URL
    lat = row["latitude"]
    lon = row["longitude"]
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"

    # Call API
    response = get(url)

    # Parse the response | Insert into Dataframe
    response_to_json = response.json()
    aqi = response_to_json["list"][0]["main"]
    df.loc[index, "aqi"] = aqi["aqi"]
    pol = response_to_json["list"][0]["components"]
    df.loc[index, "co"] = pol["co"]
    df.loc[index, "no"] = pol["no"]
    df.loc[index, "no2"] = pol["no2"]
    df.loc[index, "o3"] = pol["o3"]
    df.loc[index, "so2"] = pol["so2"]
    df.loc[index, "pm2_5"] = pol["pm2_5"]
    df.loc[index, "pm10"] = pol["pm10"]

'''PART II: Calculating the AQI According to US-EPA Standards'''
# TODO: Based on the Pollutant Concentrations, find the max AQI from them
#       Formula: max(aqi(pm2_5), aqi(pm10), aqi(co), ...)

'''PART III: Saving Dataframe to a CSV'''
# Save the Dataframe to the CSV
df.to_csv(FILE, na_rep='null', index=False)