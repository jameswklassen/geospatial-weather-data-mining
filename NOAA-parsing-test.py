from netCDF4 import Dataset

ctd = Dataset('wod_ctd_2019.nc', 'r')

Lat = ctd.variables['lat']
Lon = ctd.variables['lon']
Temperature = ctd.variables['Temperature']
Temperature_row_size = ctd.variables['Temperature_row_size']

# Casts are single "physical columns" of measurement containing multiple obs (observations)
# For example, a cast of 1 is equal to time(1), lat(1), lon(1), z[a..b] where a = z_row_size[0] and b = a + z_row_size[1], temperature[c..d] 
# where c = Temperature_row_size[0] and d = c + Temperature_row_size[1]

# For a single cast of temperature data we need "time lat lon z"

# Time
# units = "days since 1770-01-01 00:00:00 UTC"
Time = ctd.variables['time'] # casts

# Lat
# units = "degrees_north"
Lat = ctd.variables['lat'] # casts

# Lon
# units = "degrees_east"
Lon = ctd.variables['lon'] # casts

# Z
# units = "m"
# long_name = "depth_below_sea_surface"
Z = ctd.variables['z'] # obs

# Z_row_size
# long_name = "number of depth observations for this cast"
Z_row_size = ctd.variables['z_row_size'] # casts

# Temperature
Temperature = ctd.variables['Temperature'] # obs

# Temperature_row_size
# long_name = "number of Temperature observations for this cast"
Temperature_row_size = ctd.variables['Temperature_row_size'] # casts

print(Time[0])
print("Lat", Lat[0])
print("Lon", Lon[0])

for i in range(0, Temperature_row_size[0]):
  print(f"{format(Temperature[i], '0.2f')} celsius at {format(Z[i], '.0f')} metres")

# Print all the temperature data for the second lat/lon coordinate in the dataset (11 observations)
print("\n")
print(Time[1])
print("Lat", Lat[1])
print("Lon", Lon[1])

# this indexing is starting at the end of the last series of observations and ending at the end + length of the second set of observations
for i in range(Temperature_row_size[0], Temperature_row_size[0] + Temperature_row_size[1]):
  print(f"{format(Temperature[i], '0.2f')} celsius at {format(Z[i], '.0f')} metres")

# Print all the temperature data for the second lat/lon coordinate in the dataset (11 observations)
print("\n")
print(Time[2])
print("Lat", Lat[2])
print("Lon", Lon[2])

# this indexing is starting at the end of the last series of observations and ending at the end + length of the second set of observations
for i in range(Temperature_row_size[0] + Temperature_row_size[1], Temperature_row_size[0] + Temperature_row_size[1] + Temperature_row_size[2]):
  print(f"{format(Temperature[i], '0.2f')} celsius at {format(Z[i], '.0f')} metres")