# Borealis: Tracing the Origin of Air Pollution

This package contains code to use DeepMind's [GraphCast](https://www.science.org/doi/10.1126/science.adi2336) and Microsoft's [Aurora](https://arxiv.org/pdf/2405.13063), as well as code to obtain the required ERA5 weather data.

We have provided code that use the following pretrained models:

| GraphCast        | Aurora        
| :-------------: |:-------------:
| `graphcast_small`      | `aurora-0.25-pretrained` 

Model weights and normalization statistics for GraphCast have been provided; those for Aurora are being pulled from an online repository on [HuggingFace](https://huggingface.co/microsoft/aurora)

## Prerequisites

* You must register an account with the [Climate Data Store](https://cds.climate.copernicus.eu/how-to-api) and follow their steps for setting up your API Key according to your operating system.
  * Note from Developers: There **MIGHT** be some packages that do NOT get downloaded even after using both commands. Therefore, we kindly ask that you download whatever may be needed until we can build a comprehensive list of every dependency needed. One of these can be google cloud storage; if this is the case, use `pip install google-cloud-storage`.
* Microsoft's Aurora seems to only use CUDA architecture, meaning that if you do not possess an Nvidia GPU, it is **HIGHLY RECOMMENDED** you use the graphcast model. 
* As of October 05, 2024, `weather.py` and both models only use data from a predefined date and output a forecast for a predetermined time as well. The team plans on changing this in the future, but if you currently already have the computer skills to do so, you may change it **AT YOUR OWN RISK**

## Steps-to-Follow
1. Download the repository

    You can download the repository as either a zip file or by cloning using Git.

2. Create a Python Virtual Enviroment and Download Required Packages
   
   In the main directory, run `python3 -m venv .venv` to create the folder, run `source .venv/bin/activate` to enter the virtual environment, and download all the necessary packages by using the commands `pip install --upgrade https://github.com/deepmind/graphcast/archive/master.zip` for GraphCast and `pip install microsoft-aurora` for Aurora. It is **recommded** that you use both commands, as some packages found with Aurora may be in the files for GraphCast and vice versa.

3. Run setup.py

    By running `python3 setup.py`, you will create the necessary folder structure that allows the rest of the program to work

4. Download the necessary Weather Data
   
   `weather.py` is your ticket to downloading the necessary ERA5 data. However, it is currently set up to download the data in different ways depending on which model you want to use. If you plan on using Aurora, use the command `python3 weather.py aurora`. If you plan on using GraphCast, the command is `python3 weather.py graphcast`. The data itself will be downloaded in the `weather_data` folder.

5. Generate the predicted weather forecast

   Simply run either `python3 aurora_normal.py` or `graphcast_small.py` depending As of October 05, 2024, the script using the aurora model `aurora_normal.py` generates a predicted forcast for 2023-01-02 across 12 hours, while the script using the graphcast model, `graphcast_small.py`, generates a forecast for 2024-01-02 across 18 hours seperated into 4 sections [00:00, 06:00, 12:00, 18:00].

## Disclaimer:

    Since our team is barely starting this project and getting used to everything, there is still A LOT we do not know. This, unfortunately, does extend to the main files themselves. We aim to learn more about the intricacies of each model, how they work, and how we can modify them for our use case.
   
   

