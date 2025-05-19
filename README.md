# [Borealis](https://athena.cs.csub.edu/~lrojo1/): Tracking Pollution in Kern County using Weather Patterns

This package contains code that uses Microsoft's [Aurora](https://arxiv.org/pdf/2405.13063), as well as code to obtain the required ERA5 weather data.

## Prerequisites

* Register an account with the [Climate Data Store](https://cds.climate.copernicus.eu/how-to-api) and follow their steps for setting up your API Key according to your operating system.
* Register an account with [OpenWeather](https://openweathermap.org/api) (Their free tier should be sufficient), and write down your API key (will be used later).
* **NOTICE**: This program does require the use of bash scripts in order to expedite certain processes. If you are unsure of what these scripts do or are unsure if they are trustworthy, you may look through any file with the `.sh` file extenstion. Nonetheless, <ins>*IT IS UP TO YOU*</ins> to decide whether or not to trust the provided scripts.

## One More Thing ...
The following instructions are written with the idea that the user has prior knowledge with how to work with Python and the command line of your operating system. If you do not or need a refresher, we **HIGHLY** recommend doing so before continuing. Futhermore, <ins>this program has only been tested under a Linux/GNU enviroment</ins>, and while it will work on MAC OS X devices, we are uncertain of its ability to run on Windows-based machines. If you only have a Windows machine, we recommend downloading the Windows Subsystem for Linux ([WSL](https://learn.microsoft.com/en-us/windows/wsl/install)) and continuing afterwards. Finally, while not intended, this program MIGHT work if the hour or interval is not a multiple of six (think 00:00, 06:00, 12:00, and 18:00), but some problems that we may have overlooked might come up. Therefore, for the best experience, run this program sometime between the previously-stated 6-hour time intervals and continously do so after each hour until there is enough data for the program to create an evaluation. 
  
## Steps-to-Follow

1. Download the repository

   You can download the repository as either a zip file or by cloning using Git.

2. Run `source setup.sh`
   
   After downloading the repository and entering the main directory, run this command to setup the necessary conda enviroment with Python, download all required pip packages as seen in the `requirements.txt` file, activate the conda enviroment, and create every folder needed by the program.

   * Note from Developers: Some packages required to run the Aurora model **MAY NOT** be included in the requirements.txt document. If any errors occur after attempting to run the mdoel, run the command `pip install microsoft-aurora`, which should download the few remaining packages needed (mainly Nvidia-based dependencies).
  
3. Run `bash current.sh` or `bash forecast.sh`

   These two commands complete vastly different things:
   * current.sh: Will either download the current weather data from the OpenWeather API, or do the same but also compile the last 6-hours' worth of weather data into one file and download the last 6-hours' worth of air pollution data, also from the OpenWeather API, and create an evaluation for that interval. For the latter half to occur, THERE NEEDS TO BE 6-HOURS' WORTH OF DATA.
   * forecast.sh: Will download whatever weather data and air pollution data the OpenWeather API has forecasted for the next 24-hours, splitting said data into 4 sections, each seperated by 6-hour time intervals, and creating and evaluation from this data. **NOTE**: If the intent of the user is to see how the program generally works, this function should work best. 

4. Run `source done.sh`
   
   Once any operation of the program is complete, the user can exit any conda enviroments by using this commands.

   * NOTE: If the user wants to re-enter the conda enviroment set up by the program at the start, then running the command `source setup.sh` will re-enter the user into the enviroment, thereby allowing the use of the program once again. 

## Disclaimer:

   All outputs created by this program are intended to be seen via the command line. If something akin to the web interface provided by the team is needed, then it is **UP TO THE USER** to create their own web server and develop the frontend for it. 
