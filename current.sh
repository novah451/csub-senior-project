#!/bin/bash

# Runs every hour --> only weather_init.py will be called
# After every 6 hours --> weather_init.py with "dump" will run; air pollution
# information will be collected over last 6 hours; board will be created;
# evaluation will be performed over the newly-created board.json file

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux/GNU
    year=$(date +%Y)
    month=$(date +%m)
    day=$(date +%d)
    yesterday=$(date -d "1 day ago" +%d)

    hour=$(date +%H)
    p_hour=$(date -d "6 hours ago" +%H)
    midnight=$(date -d "2 hours ago" +%d)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OSX
    year=$(date +%Y)
    month=$(date -v-5M +%m)
    day=$(date +%d)
    yesterday=$(date -v-1d +%d)

    hour=$(date +"%H")
    p_hour=$(date -v-6H +%H)
fi

interval=$(( $hour % 6 ))
p_interval=$(( $interval - 1 ))

hour_minus_one=$(( $hour - 1 ))
p_hour_minus_one=$(( $p_hour - 1 ))

# If the previous interval created new files and shit and a new interval has started
# move all the old stuff to an archive folder so that everything can be added smoothly
if [[ $p_interval == 0 ]]; then

    echo $year $month $day $hour $p_hour $midnight
    echo log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"
    echo log/components/current/"*" log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"

    if [ -d "log/components/archive/current/"$year"-"$month"-"$midnight"" ]; then
        echo "Parent Directory exists."
        mkdir log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"
        mv log/components/current/* log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"
    else
        mkdir log/components/archive/current/"$year"-"$month"-"$midnight"
        mkdir log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"
        mv log/components/current/* log/components/archive/current/"$year"-"$month"-"$midnight"/"$p_hour_minus_one"-"$hour_minus_one"
    fi

fi

if [[ $interval == 0 ]]; then
    python3 weather_init.py $year $month $day $hour dump
    python3 aqi.py $year $month $day $hour
    python3 board_init.py $year $month $day $hour
    python3 evaluate_init.py $year $month $day $hour
else
    python3 weather_init.py $year $month $day $hour no
fi