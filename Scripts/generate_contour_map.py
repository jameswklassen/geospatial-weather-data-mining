import matplotlib.pyplot as plt
from matplotlib import colors, cm
import cartopy.crs as ccrs

from netCDF4 import Dataset

FILENAME = 'EAR5-01-01-2020.nc'

OUTPUT_DIR = 'output'
OUTPUT_FORMATS = ['svg', 'png']

MARKER_SIZE = 3
MARKER = ","

TOTAL_LAT = 180
TOTAL_LON = 360

KELVIN = 271


def save_file(name):
    """Save the current plot as an .svg in the image directory"""

    for output_format in OUTPUT_FORMATS:
        path = f"{OUTPUT_DIR}/{name}.{output_format}"
        print(f"Writing {path}")
        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def plot_contour(data, title, cmap):
    plt.suptitle(title, fontsize=16)
    ax = plt.axes(projection=ccrs.PlateCarree(), label=title)
    plt.contourf(lons, lats, data, 60, transform=ccrs.PlateCarree(), cmap=cmap)
    ax.coastlines()

    norm = colors.Normalize(vmin=min(data.flatten()), vmax=max(data.flatten()))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, shrink=0.5)

    save_file(title)


if __name__ == '__main__':
    dataset = Dataset(FILENAME, 'r')

    lats = dataset.variables['latitude'][:]
    lons = dataset.variables['longitude'][:]
    sea_surface_temperature = dataset.variables['sst'][0, :, :]
    mean_sea_level_pressure = dataset.variables['msl'][0, :, :]
    two_metre_temperature = dataset.variables['t2m'][0, :, :]
    total_cloud_cover = dataset.variables['tcc'][0, :, :]

    plot_contour(sea_surface_temperature, 'sea_surface_temperature', cm.jet)
    plot_contour(mean_sea_level_pressure, 'mean_sea_level_pressure', cm.BuPu)
    plot_contour(two_metre_temperature, 'two_metre_temperature', cm.jet)
    plot_contour(total_cloud_cover, 'total_cloud_cover', cm.get_cmap('Blues_r')) # _r for reversed color map
