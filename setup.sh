#!/bin/bash

if [ ! -d "miniconda3" ]; then
    echo "miniconda3 directory does not exist."
    mkdir -p miniconda3
    curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o miniconda3/miniconda.sh
    bash miniconda3/miniconda.sh -b -u -p miniconda3
    rm miniconda3/miniconda.sh
fi

if [ ! -d "miniconda3/envs/borealis" ]; then
    conda create -n borealis python=3.12.6
fi

source miniconda3/bin/activate
conda activate borealis

if [[ $(pip freeze | grep 'microsoft-aurora') = "" ]]; then
    pip install -r requirements.txt
fi

if [ ! -d "log" ]; then
    python3 folders.py
fi

if [ ! -f ".env" ]; then
    echo 'OPENWEATHERMAP_API_KEY=""' > .env
fi
