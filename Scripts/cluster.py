from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import argparse
import errno
import json
from random import randint
import multiprocessing as mp
import numpy as np
from consts import TOTAL_LAT, TOTAL_LON, VARIABLES, CONVERTED_DIRECTORY, CLUSTERED_DIRECTORY, DEFAULT_K

DEBUG = False


def choose_random_duplicate(clustermeans, index, backwards):
    """Break ties for clusters with identical means"""

    if not backwards:
        duplicate_count = 0
        for i in range(index+1, len(clustermeans)):
            if clustermeans[i] == clustermeans[index]:
                duplicate_count += 1

        # If we have duplicates, randomly choose one to assign the datapoint to
        if duplicate_count > 0:
            return randint(index, index + duplicate_count)
        else:
            return index
    else:
        duplicate_count = 0
        for i in range(index-2, -1, -1):
            if clustermeans[i] == clustermeans[index-1]:
                duplicate_count += 1

        # If we have duplicates, randomly choose one to assign the datapoint to
        if duplicate_count > 0:
            return randint(index - duplicate_count - 1, index-1)
        else:
            return index-1


def closest_search(datapoint, clustermeans):
    # Finds the lowest index such that datapoint <= clustermeans[index]
    index = np.searchsorted(clustermeans, datapoint)

    # If the index is zero, then it's equal or smaller than the smallest element.
    if index == 0:
        return choose_random_duplicate(clustermeans, index, False)

    # If the index is equal to the array length then it's larger than the largest element.
    if index == len(clustermeans):
        return choose_random_duplicate(clustermeans, index, True)

    # Now we have that datapoint <= clustermeans[index] && index > 0
    # Check which is closer: index or index-1
    ind_diff = abs(clustermeans[index] - datapoint)
    indm1_diff = abs(clustermeans[index-1] - datapoint)

    # If ind_diff == indm1_diff then the datapoint is *exactly* halfway between the two
    if ind_diff == indm1_diff:
        return randint(index-1, index)
    elif ind_diff < indm1_diff:
        return choose_random_duplicate(clustermeans, index, False)
    else:
        return choose_random_duplicate(clustermeans, index, True)


def cluster(data, k):
    """
    cluster

    algorithm overview:
        1: Choose k random points, assign the mean of each cluster to the value of its single data point
        2: Assign each data point its cluster based on which mean is closest
        3: Calculate the new means for each cluster based on the data points inside
        4: If the new means are different than the previous means, repeat from step 2
    """

    # 1: Choose k random points (sea surface temperature)
    means = np.zeros(k)
    new_means = np.zeros(k)

    cluster_points = [np.zeros(TOTAL_LAT*TOTAL_LON) for i in range(k)]
    cluster_count = [0 for i in range(k)]

    for i in range(k):
        x = None
        while x is None:
            x = data[randint(0, TOTAL_LAT-1)][randint(0, TOTAL_LON-1)]
        new_means[i] = x

    # Sort means by magnitude
    new_means.sort()

    if DEBUG:
        print(new_means)

    while not np.array_equal(means, new_means):
        means = new_means.copy()
        new_means = np.zeros(k)

        # 2: Assign each value to whichever mean is closest (random tiebreaker)
        for i in range(TOTAL_LAT):
            for j in range(TOTAL_LON):
                if data[i][j] is None:
                    continue
                cluster = closest_search(data[i][j], means)
                cluster_points[cluster][cluster_count[cluster]] = data[i][j]
                cluster_count[cluster] += 1

        if DEBUG:
            print(cluster_count)

        # 3: Calculate new cluster means
        for i in range(k):
            new_means[i] = np.resize(cluster_points[i], cluster_count[i]).mean()

            # Reset cluster count to prevent bad things
            cluster_count[i] = 0

        new_means.sort()

        # 4: If means are different than new means, go back to 2

    # We now have the final clustering - display the means of each cluster!
    if DEBUG:
        print(new_means)

    # For each data point, find its cluster and make the value of the data point equal to the mean of the cluster.
    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] is None:
                continue
            cluster = closest_search(data[i][j], new_means)
            data[i][j] = new_means[cluster]

    min = np.nanmin(np.array(data, dtype=np.float64))
    max = np.nanmax(np.array(data, dtype=np.float64))

    return (data, min, max)


def cluster_file(filename, k, output_dir):
    """
    Given a filename and k value, run fcluster on the file and write to output_dir

    returns the min/max values for each variable
    """
    if DEBUG:
        print('Clustering', filename)

    with open(filename, 'r') as my_file:
        data = json.load(my_file)

    ranges = {}     # keep track of min/max values for each variable

    for variable in VARIABLES:
        data[variable], min, max = cluster(data[variable], k)
        ranges[variable] = (min, max)

    # Write clustered data to new .json file
    with open(f"{output_dir}/{basename(filename)}", 'w') as outfile:
        json.dump(data, outfile)

    return ranges


def get_variable_ranges(results):
    """Calculate the max/min value of each clustered variable"""

    ranges = {var: {'min': [], 'max': []} for var in VARIABLES}

    for result in results:
        for var, val in result.items():
            local_min, local_max = val
            ranges[var]['min'].append(local_min)
            ranges[var]['max'].append(local_max)

    for var, val in ranges.items():
        ranges[var] = (min(val['min']), max(val['max']))

    return ranges


def init(output_dir):
    """Initialization for the algorithm"""

    # Create the output directory if it doesn't exist
    try:
        makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input JSON file')
    parser.add_argument('-o', '--output', help='Output subdirectory')
    parser.add_argument('-k', '--k', help='k value', default=DEFAULT_K)
    args = parser.parse_args()

    # If we specify a custom output dir, place it inside the default output directory
    output_dir = f"{CLUSTERED_DIRECTORY}/{args.output}" if args.output else CLUSTERED_DIRECTORY

    init(output_dir)

    args.k = int(args.k)

    # If input is a single file, easy case
    if args.input and isfile(args.input):
        print('Cluster', args.input, output_dir)
        cluster_file(args.input, args.k)
        exit()

    # Since input isn't a single file, it's either
    #   a) a directory, or
    #   b) not specified
    input_dir = args.input if args.input and isdir(args.input) else CONVERTED_DIRECTORY

    print('Cluster files in', input_dir)

    # Collect all the .json files in input_dir
    files = [f"{input_dir}/{f}" for f in listdir(input_dir) if isfile(join(input_dir, f)) if f.endswith('json')]

    pool = mp.Pool(mp.cpu_count())
    results = pool.starmap(cluster_file, [(file, args.k, output_dir) for file in files])

    # Calculate min/max across the clusters for each variable
    ranges = get_variable_ranges(results)

    with open(f"{output_dir}/range.json", 'w') as outfile:
        json.dump(ranges, outfile)
