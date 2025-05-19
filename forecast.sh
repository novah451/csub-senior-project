#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux/GNU
    year=$(date +%Y)
    month=$(date +%m)
    day=$(date +%d)
    yesterday=$(date -d "1 day ago" +%d)

    init_month=$(date -d "6 days ago" +%m)
    init_day=$(date -d "6 days ago" +%d)

    auto_month=$(date +%m)
    auto_day=$(date +%d)

    hour=$(date +"%H")
    p_hour=$(date -d "6 hours ago" +%H)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS X
    year=$(date +%Y)
    month=$(date +%m)
    day=$(date +%d)
    init=$(date -v-6d +%d)
    yesterday=$(date -v-1d +%d)

    hour=$(date +"%H")
    p_hour=$(date -v-6H +%H)
fi

rm weather_data/aurora/*.nc
mkdir log/components/archive/forecast/"$year"-"$month"-"$day"
mv log/components/forecast/* log/components/archive/forecast/"$year"-"$month"-"$day"

python3 weather.py $year $init_month $init_day
python3 aurora_init.py $year $init_month $init_day

for i in $(seq 1 6);
do
    if [[ "$i" -lt 6 ]]; then
        python3 aurora_auto.py 4
    elif [[ "$i" -eq 6 ]]; then
        python3 aurora_auto.py 5
    fi
done

python3 localize_auto.py $year $auto_month $auto_day
python3 filter_auto.py $year $auto_month $auto_day 12
python3 aqi_auto.py $year $auto_month $auto_day 12
python3 board_auto.py $year $auto_month $auto_day 12
python3 evaluate_auto.py $year $auto_month $auto_day 12
