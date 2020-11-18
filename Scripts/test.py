from netCDF4 import Dataset

ctd = Dataset('EAR5-01-01-2020.nc', 'r')

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

for j in range(0, len(lon)):
    for i in range(0, len(lat)):
        print(
                f"""
                lat: {lat[i]}, lon: {lon[j]}:
                land-sea mask: {format(land_sea_mask[0, i, j], '.2f')}
                ten metre U wind component: {format(ten_metre_U_wind_component[0, i, j], '.2f')}
                ten metre V wind component: {format(ten_metre_V_wind_component[0, i, j], '.2f')}
                2 metre temperature: {format(two_metre_temperature[0, i, j]-271, '.2f')}
                mean sea level pressure: {format(mean_sea_level_pressure[0, i, j], '.2f')}
                mean wave direction: {format(mean_wave_direction[0, i, j], '.2f')}
                sea surface temp: {format(sea_surface_temperature[0, i, j]-271, '.2f')}
                total cloud cover: {format(total_cloud_cover[0, i, j], '.2f')}
                """
            )
