from netCDF4 import Dataset
from utilities import get_cast_obs

ctd = Dataset('datasets/NOAA/Test/wod_ctd_2019.nc', 'r')

# Casts are single "physical columns" of measurement containing multiple obs
# (observations).
# For example, a cast of 1 is equal to time(1), lat(1), lon(1), z[a..b] where
# a = z_row_size[0] and b = a + z_row_size[1], temperature[c..d].
# where c = Temperature_row_size[0] and d = c + Temperature_row_size[1]

# For a single cast of temperature data we need "time lat lon z"

# Time
# units = "days since 1770-01-01 00:00:00 UTC"
Time = ctd.variables['time']  # casts

# Lat
# units = "degrees_north"
Lat = ctd.variables['lat']  # casts

# Lon
# units = "degrees_east"
Lon = ctd.variables['lon']  # casts

# Z
# units = "m"
# long_name = "depth_below_sea_surface"
Z = ctd.variables['z']  # obs

# Z_row_size
# long_name = "number of depth observations for this cast"
Z_row_size = ctd.variables['z_row_size']  # casts

# Temperature
Temperature = ctd.variables['Temperature']  # obs

# Temperature_row_size
# long_name = "number of Temperature observations for this cast"
Temperature_row_size = ctd.variables['Temperature_row_size']  # casts

cast_one_temperatures = get_cast_obs(0, Temperature, Temperature_row_size)
cast_one_z = get_cast_obs(0, Z, Z_row_size)
cast_two_temperatures = get_cast_obs(1, Temperature, Temperature_row_size)
cast_two_z = get_cast_obs(1, Z, Z_row_size)
cast_three_temperatures = get_cast_obs(2, Temperature, Temperature_row_size)
cast_three_z = get_cast_obs(2, Z, Z_row_size)

print("Date:", Time[0])
print("Lat:", Lat[0])
print("Lon:", Lon[0])

for i in range(0, len(cast_one_temperatures)):
    print(f"{format(cast_one_temperatures[i], '0.2f')} celsius at {format(cast_one_z[i], '.0f')} metres")

print("\n")
print("Date:", Time[1])
print("Lat:", Lat[1])
print("Lon:", Lon[1])

for i in range(0, len(cast_two_temperatures)):
    print(f"{format(cast_two_temperatures[i], '0.2f')} celsius at {format(cast_two_z[i], '.0f')} metres")

print("\n")
print("Date:", Time[2])
print("Lat:", Lat[2])
print("Lon:", Lon[2])

for i in range(0, len(cast_three_temperatures)):
    print(f"{format(cast_three_temperatures[i], '0.2f')} celsius at {format(cast_three_z[i], '.0f')} metres")
