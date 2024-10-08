# Borealis: Tracing the Origin of Air Pollution

This package contains code to use DeepMind's [GraphCast](https://www.science.org/doi/10.1126/science.adi2336) and Microsoft's [Aurora](https://arxiv.org/pdf/2405.13063), as well as code to obtain the required ERA5 weather data.

We have provided code that use the following pretrained models:

| GraphCast        | Aurora        
| :-------------: |:-------------:
| `graphcast_small`      | `aurora-0.25-pretrained` 

## Prerequisites

* You must register an account with the [Climate Data Store](https://cds.climate.copernicus.eu/how-to-api) and follow their steps for setting up your API Key according to your operating system.
* Microsoft's Aurora seems to only use CUDA architecture, meaning that if you do not possess an Nvidia GPU, it is **HIGHLY RECOMMENDED** you use the graphcast model. 
* NOTICE: `weather.py` and both models only use data from a predefined date and output a forecast for a predetermined time as well. The team plans on changing this in the future, but if you currently already have the computer skills to do so, you may change it **AT YOUR OWN RISK**

## Steps-to-Follow
1. Download the repository

    You can download the repository as either a zip file or by cloning using Git.

2. Create a Python Virtual Enviroment and Download Required Packages
   
   In the main directory, run `python3 -m venv .venv` to create the folder, run `source .venv/bin/activate` to enter the virtual environment, and download all the necessary packages by using the commands `pip install --upgrade https://github.com/deepmind/graphcast/archive/master.zip` for GraphCast and `pip install microsoft-aurora` for Aurora. It is **recommded** that you use both commands, as some packages found with Aurora may be in the files for GraphCast and vice versa.

   * Note from Developers: There **MIGHT** be some packages that do NOT get downloaded even after using both commands. Therefore, we kindly ask that you download whatever may be needed until we can build a comprehensive list of every dependency needed. One of these can be google cloud storage; if this is the case, use `pip install google-cloud-storage`.

3. Run the setup file: `python3 setup.py`

   Running this file generates the folder structure required for the program. It also downloads any files required by either model to work locally.

4. Download Weather Data: `python3 weather.py [MODEL]`
   
   `weather.py` is your ticket to downloading the necessary ERA5 data. However, it is currently set up to download the data in different ways depending on which model you want to use. If you plan on using Aurora, use the command `python3 weather.py aurora`. If you plan on using GraphCast, the command is `python3 weather.py graphcast`. The data itself will be downloaded in the `weather_data` folder.

5. Generate the predicted weather forecast

   Run `python3 aurora_normal.py` to use the **Aurora** model or `python3 graphcast_small.py` for **GraphCast**. For now, `aurora_normal.py` generates a predicted forcast for 2023-01-02 across 12 hours, while `graphcast_small.py` generates a forecast for 2024-01-02 across 18 hours seperated into 4 sections [00:00, 06:00, 12:00, 18:00].

## Disclaimer:

   This project is still in the very early stages of devlopment. We plan on adding more/doing more with what we have provided. There is still A LOT we do not know. As development continues, we plan on updating this respository with any new features that we add/come up with.
   
   

