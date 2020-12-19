from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import errno
import json
import argparse
import numpy as np
import multiprocessing as mp
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import colors, cm
import cartopy.crs as ccrs
from consts import TOTAL_LAT, TOTAL_LON, OUTPUT_DIRECTORY

DEBUG = False

INPUT_DIRECTORY = OUTPUT_DIRECTORY + '/converted'
IMG_DIRECTORY = OUTPUT_DIRECTORY + '/img'

OUTPUT_FORMATS = ['png']
COLOR_LEVELS = 60
CORNER_SMOOTHING = False

lons = [i+1.375 for i in range(TOTAL_LON)]
lats = [i-1.375 for i in range(int(TOTAL_LAT/2), int(-TOTAL_LAT/2), -1)]


def save_file(dir, name):
    """Save the current plot as an .svg in the image directory"""

    dir_path = f"{IMG_DIRECTORY}/{dir}"
    try:
        makedirs(dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for output_format in OUTPUT_FORMATS:
        path = f"{dir_path}/{name}.{output_format}"

        if DEBUG:
            print(f"Writing {path}")

        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def color_map(var):
    if var == 'mean_sea_level_pressure':
        return cm.BuPu
    elif var == 'total_cloud_cover':
        return cm.get_cmap('Blues_r')
    else:
        return cm.jet


def plot(data, variable, day, cmap, output_dir=None, range=None):
    """Plot a single variable on a single day"""

    title = variable
    min, max = range

    plt.suptitle(title, fontsize=16)
    ax = plt.axes(projection=ccrs.PlateCarree(), label=f"{title}-{day}")
    plt.contourf(
        lons,
        lats,
        data,
        COLOR_LEVELS,
        transform=ccrs.PlateCarree(),
        vmin=min,
        vmax=max,
        cmap=cmap,
        corner_mask=CORNER_SMOOTHING,
    )

    textstr = day_str(day)
    plt.text(0.4, 0.9, textstr, fontsize=12, transform=plt.gcf().transFigure)

    ax.coastlines()

    if range:
        norm = colors.Normalize(vmin=min, vmax=max)
    else:
        norm = colors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, shrink=0.5)

    file_dir = f"{output_dir}/{variable}" if output_dir else variable
    save_file(file_dir, day)


def day_str(day):
    """
    Convert an integer day to a date string with format <Month Date>
    e.g. 1 -> "Jan 1"
    """
    padded = f"{int(day)+1:03d}"

    dt = datetime.strptime(padded, "%j")
    return dt.strftime("%B %d")


def generate_plots(filename, output_dir=None, range=None):
    """Generate plots for all variables given a .json file"""

    if DEBUG:
        print('Generating plot for', filename)

    with open(filename, 'r') as my_file:
        json_data = my_file.read()
        data = json.loads(json_data)

    day = basename(filename).split('.')[0]

    for variable in data.keys():
        min, max = range[variable]
        plot(
            np.array(data[variable], dtype=np.float64),
            variable,
            day,
            color_map(variable),
            output_dir=output_dir,
            range=range[variable]
        )


def init():
    try:
        makedirs(OUTPUT_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    try:
        makedirs(IMG_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input JSON file")
    parser.add_argument("-o", "--output", help="Output subdirectory", default=None)
    args = parser.parse_args()

    init()

    # If input is a single file, easy case
    if args.input and isfile(args.input):
        generate_plots(args.input, args.output)
        exit()

    # Since input isn't a single file, it's either
    #   a) a directory, or
    #   b) not specified
    input_dir = args.input if args.input and isdir(args.input) else INPUT_DIRECTORY

    print("Generating plots for all .json files in", input_dir)

    # Collect all the .json files in input_dir
    files = [f"{input_dir}/{f}" for f in listdir(input_dir) if isfile(join(input_dir, f)) if f.endswith('json') if not f.startswith('range')]

    with open(f"{input_dir}/range.json", 'r') as my_file:
        json_data = my_file.read()
        range = json.loads(json_data)

    pool = mp.Pool(mp.cpu_count())
    pool.starmap(generate_plots, [(file, args.output, range) for file in files])
