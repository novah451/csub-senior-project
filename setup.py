from borealis import setup_folders
from borealis import PrettyCLI
from borealis import download_weather
from borealis import aqi
from dotenv import load_dotenv

import os

load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

PrettyCLI.tprint("Hello! This is the setup script from Project Borealis \n")

# 1. Setup the folder structure
setup_folders()

# 2. Ask the user which model they want to use; determines how weather input is downloaded
PrettyCLI.tprint("Excellent! Now, which model do you intend on using?")
PrettyCLI.spprint("[1] Aurora")
PrettyCLI.spprint("[2] GraphCast")
PrettyCLI.spprint("[3] Both")

while True:
    try:
        dataset = PrettyCLI.tinput("Option: ")
    except ValueError:
        PrettyCLI.spprint("Sorry, I didn't understand that.")
        continue
    else:
        if dataset not in range(1, 4):
            PrettyCLI.spprint("Not a valid option, Try Again")
            continue
        else:
            PrettyCLI.tprint("Very well, getting right to it\n")
            break

download_weather(dataset)
PrettyCLI.tprint("Requested weather input data successfully downloaded!")

# 3. Download and save AQI data for kern county
PrettyCLI.tprint("Now downloading required AQI information")
aqi(API_KEY)
PrettyCLI.tprint("AQI information successfully downloaded!")
