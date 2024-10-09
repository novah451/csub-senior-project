# Borealis: Tracing the Origin of Air Pollution

This package contains code to use DeepMind's [GraphCast](https://www.science.org/doi/10.1126/science.adi2336) and Microsoft's [Aurora](https://arxiv.org/pdf/2405.13063), as well as code to obtain the required ERA5 weather data.

We have provided code that use the following pretrained models:

| GraphCast        | Aurora        
| :-------------: |:-------------:
| `graphcast_small`      | `aurora-0.25-pretrained` 

## Prerequisites

* You must register an account with the [Climate Data Store](https://cds.climate.copernicus.eu/how-to-api) and follow their steps for setting up your API Key according to your operating system.
* Microsoft's Aurora seems to only use CUDA architecture for now. Therefore, if you are not using a Nvidia GPU, you can **ONLY** use the graphcast model. 
* NOTICE: `weather.py` and both models only use data from a predefined date and output a forecast for a predetermined time as well. The team plans on changing this in the future, but if you currently already have the computer skills to do so, you may change it **AT YOUR OWN RISK**

## Steps-to-Follow
1. Download the repository

   You can download the repository as either a zip file or by cloning using Git.

2. Create a Python Virtual Enviroment and Download Required Packages
   
   In the main directory, run `python3 -m venv .venv` to create the folder and use `source .venv/bin/activate` to enter the virtual environment. To download all the necessary packages, use the command `pip install -r requirements.txt`.

   * Note from Developers: Some packages required to run the Aurora model are **NOT** included in the requirements.txt document. If you would like to run this model, run the command `pip install microsoft-aurora`, which should download the few remaining packages needed (mainly Nvidia-based dependencies).
  
3. Run the setup file: `python3 setup.py`

   Running this file generates the folder structure required for the program. It also downloads any files required by either model to work locally.

4. Download Weather Data: `python3 weather.py [MODEL]`
   
   `weather.py` is your ticket to downloading the necessary ERA5 data. However, it is currently set up to download the data in different ways depending on which model you want to use. If you plan on using Aurora, use the command `python3 weather.py aurora`. If you plan on using GraphCast, the command is `python3 weather.py graphcast`. The data itself will be downloaded in the `weather_data` folder.

5. Generate the predicted weather forecast

   Run `python3 aurora_normal.py` to use the **Aurora** model or `python3 graphcast_small.py` for **GraphCast**. For now, `aurora_normal.py` generates a predicted forcast for 2023-01-02 across 12 hours, while `graphcast_small.py` generates a forecast for 2024-01-02 across 18 hours seperated into 4 sections [00:00, 06:00, 12:00, 18:00].

## Disclaimer:

   This project is still in the very early stages of devlopment. We plan on adding more/doing more with what we have provided. There is still A LOT we do not know. As development continues, we plan on updating this respository with any new features that we add/come up with.
   
   

