from netCDF4 import Dataset
import numpy as np

filename = 'EAR5-01-01-2020.nc'

ctd = Dataset(filename, 'r')

NUM_SLICES = 4
SLICE_SIZE = 0.25

KELVIN = 271

TOTAL_LAT = 180
TOTAL_LON = 360

lat = ctd.variables['latitude']
lon = ctd.variables['longitude']
land_sea_mask = ctd.variables['lsm']
ten_metre_U_wind_component = ctd.variables['u10']
ten_metre_V_wind_component = ctd.variables['v10']
two_metre_temperature = ctd.variables['t2m']
mean_sea_level_pressure = ctd.variables['msl']
mean_wave_direction = ctd.variables['mwd']
sea_surface_temperature = ctd.variables['sst']
total_cloud_cover = ctd.variables['tcc']


coordinates = [[0]*TOTAL_LON for _ in range(TOTAL_LAT)]


count = 0
MAX = 1000
for curr_lat in range(TOTAL_LAT):

    if count > MAX:
        break
    for curr_lon in range(TOTAL_LON):
        if count > MAX:
            break
        count += 1

        # Store the averages
        all_land_sea_mask = []
        all_ten_metre_U_wind_component = []
        all_ten_metre_V_wind_component = []
        all_two_metre_temperature = []
        all_mean_sea_level_pressure = []
        all_mean_wave_direction = []
        all_sea_surface_temperature = []
        all_total_cloud_cover = []

        for lat_slice in range(NUM_SLICES):
            for lon_slice in range(NUM_SLICES):
                all_land_sea_mask.append(land_sea_mask[0, lat[lat_slice], lon[lon_slice]])
                all_ten_metre_U_wind_component.append(ten_metre_U_wind_component[0, lat[lat_slice], lon[lon_slice]])
                all_ten_metre_V_wind_component.append(ten_metre_V_wind_component[0, lat[lat_slice], lon[lon_slice]])
                all_two_metre_temperature.append(two_metre_temperature[0, lat[lat_slice], lon[lon_slice]] - KELVIN)
                all_mean_sea_level_pressure.append(mean_sea_level_pressure[0, lat[lat_slice], lon[lon_slice]])
                all_mean_wave_direction.append(mean_wave_direction[0, lat[lat_slice], lon[lon_slice]])
                all_sea_surface_temperature.append(sea_surface_temperature[0, lat[lat_slice], lon[lon_slice]] - KELVIN)
                all_total_cloud_cover.append(total_cloud_cover[0, lat[lat_slice], lon[lon_slice]])

        coordinates[curr_lat][curr_lon] = {
            'lat': curr_lat,
            'lon': curr_lon,
            'sea_surface_temperature': np.mean(all_sea_surface_temperature),
            'land_sea_mask': np.mean(all_land_sea_mask),
            'ten_metre_U_wind_component': np.mean(all_ten_metre_U_wind_component),
            'ten_metre_V_wind_component': np.mean(all_ten_metre_V_wind_component),
            'two_metre_temperature': np.mean(all_two_metre_temperature),
            'mean_sea_level_pressure': np.mean(all_mean_sea_level_pressure),
            'mean_wave_direction': np.mean(all_mean_wave_direction),
            'sea_surface_temperature': np.mean(all_sea_surface_temperature),
            'total_cloud_cover': np.mean(all_total_cloud_cover),
        }

print(coordinates)
