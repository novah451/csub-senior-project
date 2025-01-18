#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux/GNU
    year=$(date -d "1 year ago" +%Y)
    month=$(date +%m)
    day=$(date +%d)
    yesterday=$(date -d "1 day ago" +%d)

    hour=$(date +"%H")
    p_hour=$(date -d "6 hours ago" +%H)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OSX
    year=$(date -v-1y +%Y)
    month=$(date +%m)
    day=$(date +%d)
    yesterday=$(date -v-1d +%d)

    hour=$(date +"%H")
    p_hour=$(date -v-6H +%H)
fi

echo $year $month $day $yesterday $hour $p_hour

if [[ "$hour" -eq 12 ]]; then
    # cleanup some stuff first
    rm weather_data/aurora/*.nc
    rm predictions/aurora/*_predictions_$year-$month-$yesterday.csv

    python3 weather.py $year $month $day 
    python3 aurora_normal.py $year $month $day 
    python3 localize.py $year $month $day
fi

python3 aqi.py $year $month $day $hour 
python3 filter.py $year $month $day $hour
python3 board.py $year $month $day $hour
python3 evaluate.py $year $month $day $hour

# cleaning up old files
rm log/components/*_*-$p_hour.*
