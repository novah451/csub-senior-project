import csv

with open("./predictions/graphcast/predictions.csv", "r") as csvfile:
    read = csv.DictReader(csvfile)


    with open("./predictions/graphcast/kernPredictions.csv", "w", newline='') as outfile:
        fieldnames = ['time','lat','lon','batch','level',
                      '10m_u_component_of_wind','10m_v_component_of_wind',
                      '2m_temperature','geopotential','mean_sea_level_pressure',
                      'specific_humidity','temperature','total_precipitation_6hr',
                      'u_component_of_wind','v_component_of_wind','vertical_velocity']

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in read:
            if(float(row['lat']) >= 34 and float(row['lat']) <= 36 and float(row['lon']) >= 239 and float(row['lon']) <= 242):
                writer.writerow(row)
