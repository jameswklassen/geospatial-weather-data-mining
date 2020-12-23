from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import argparse
import errno
import json
from random import randint
import multiprocessing as mp
import numpy as np
from consts import TOTAL_LAT, TOTAL_LON, VARIABLES, CONVERTED_DIRECTORY, FCLUSTERED_DIRECTORY, DEFAULT_K

DEBUG = False


def unique_array(arr):
    return len(arr) == len(set(arr))


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


def closest_search_naive(datapoint, clustermeans):
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


def closest_search_no_dups(datapoints, k, means, cluster_sums, cluster_count):
    """
    closest_search_no_dups

    parameters:
     - datapoints : all datapoints (sorted as a numpy array),
     - means, sums and counts for all clusters

    returns:
     - updated cluster_means, cluster_sums and cluster_counts
    """

    # Find all cluster positions - O(k)
    cluster_sums = cluster_sums.copy()
    cluster_count = cluster_count.copy()

    dividerpos = [0]*(k-1)

    dividerpos[0] = cluster_count[0]

    for i in range(1, k-1):
        dividerpos[i] = dividerpos[i-1] + cluster_count[i]

    # Step 1: Find the average between every two adjacent cluster means - O(k)
    cluster_inbetweens = [0]*(k-1)
    for i in range(k-1):
        cluster_inbetweens[i] = (means[i]+means[i+1])/2

    n = 0

    # There is now a one-to-one correlation between dividerpos[i] and cluster_inbetweens[i].
    # Now we can start the main loop: For each cluster, determine its new divider location
    # and modify its sum and count.
    for i in range(k-1):
        n += 1
        
        # If it's to the left, then datapoints[dividerpos-1] >= cluster_inbetweens[i]
        # If it's to the right, then 
        if datapoints[dividerpos[i]-1] >= cluster_inbetweens[i]:
            # print("It's to the left!")

            # Iterate until we have that datapoints[dividerpos-1] < cluster_inbetweens[i]
            # Each time, we "move it to the left" by 1, we need to adjust the cluster sum and cluster count for the two clusters
            # that the divider divides.
            j = dividerpos[i]
            while datapoints[j-1] >= cluster_inbetweens[i]:
                # Move the point to the right by 1
                # Subtract one item from the i'th cluster and add one from to the i+1'th cluster
                cluster_count[i] -= 1
                cluster_count[i+1] += 1
                cluster_sums[i] -= datapoints[j-1]
                cluster_sums[i+1] += datapoints[j-1]

                j -= 1
                n += 1
        elif datapoints[dividerpos[i]] < cluster_inbetweens[i]:
            # print("It's to the right!")
            # Iterate until we have that datapoints[dividerpos] >= cluster_inbetweens[i]
            # Each time, we "move it to the right" by 1, we need to adjust the cluster sum and cluster count
            # for the two clusters that the divider divides.
            j = dividerpos[i]
            while datapoints[j] < cluster_inbetweens[i]:
                # Move the point to the right by 1
                # Add one item to the i'th cluster and remove one from the i+1'th cluster
                cluster_count[i] += 1
                cluster_count[i+1] -= 1
                cluster_sums[i] += datapoints[j]
                cluster_sums[i+1] -= datapoints[j]

                j += 1
                n += 1

    return (cluster_sums, cluster_count, n)


def cluster_fast_dataset(dataset, cluster_count):
    """
    cluster_fast_dataset

    parameters:
     - dataset : dataset to cluster
     - cluster_count : TODO 

    returns:
     - updated cluster_means, cluster_sums and cluster_counts
    """
    # Sort the dataset
    dataset.sort()

    # Get the minimum and maximum
    minimum = dataset[0]
    maximum = dataset[len(dataset)-1]

    new_means = np.zeros(cluster_count)

    # Simple linear interpolation
    for i in range(cluster_count):
        new_means[i] = (i/cluster_count)*maximum + (1-i/cluster_count)*minimum

    # Get each datapoint in its respective cluster
    cluster_counts = [0]*cluster_count
    cluster_sums = [0]*cluster_count
    for i in range(len(dataset)):
        index = closest_search_naive(dataset[i], new_means)
        cluster_counts[index] += 1
        cluster_sums[index] += dataset[i]

    # If there is an empty cluster (or multiple) just get rid of it.
    # Believe it or not, this is the "industry standard" approach.
    while 0 in cluster_counts:
        index = cluster_counts.index(0)
        del cluster_counts[index]
        del cluster_sums[index]
        new_means = np.delete(new_means, index)
        cluster_count -= 1

    # Update means
    for i in range(cluster_count):
        new_means[i] = cluster_sums[i] / cluster_counts[i]

    means = np.zeros(cluster_count)

    # Now do iterations
    x_sum = 0
    iters = 0
    iter_absolute = 0
    while not np.array_equal(means, new_means):
        iter_absolute += 1
        # print(f"Iteration {iter_absolute}")
        means = new_means.copy()
        new_means = np.zeros(cluster_count)

        # If each cluster is unique then use our fast algorithm.
        if unique_array(means):
            (cluster_sums, cluster_counts, x) = closest_search_no_dups(
                dataset, cluster_count, means, cluster_sums, cluster_counts
            )

            iters += 1
            x_sum += x
            pass
        else:
            # Use the slow algorithm
            # print("Using slow method")
            cluster_counts = [0]*cluster_count
            cluster_sums = [0]*cluster_count

            for i in range(len(dataset)):
                index = closest_search_naive(dataset[i], new_means)
                cluster_counts[index] += 1
                cluster_sums[index] += dataset[i]

        # If there is an empty cluster (or multiple) just get rid of it.
        # Believe it or not, this is the "industry standard" approach.
        while 0 in cluster_counts:
            index = cluster_counts.index(0)
            del cluster_counts[index]
            del cluster_sums[index]
            means = np.delete(means, index)
            new_means = np.delete(new_means, index)
            cluster_count -= 1

        # Recalculate means
        for i in range(cluster_count):
            new_means[i] = cluster_sums[i] / cluster_counts[i]

    # End of while loop - we've reached a stable configuration
    # Return new means and average x value
    return (new_means, iters, x_sum)


def fcluster(data, k):
    """
    fcluster

    algorithm overview:
        1: Choose k random points, assign the mean of each cluster to the value of its single data point
        2: Assign each data point its cluster based on which mean is closest
        3: Calculate the new means for each cluster based on the data points inside
        4: If the new means are different than the previous means, repeat from step 2
    """

    # 1: Choose k random points (sea surface temperature)
    # data = full_data[VARIABLES[4]]

    # Use O(n log n) time to determine cluster sums and cluster counts
    data_ordered = np.zeros(TOTAL_LAT * TOTAL_LON)
    data_ordered.fill(-32767)

    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] is not None:
                data_ordered[i*TOTAL_LON+j] = data[i][j]

    data_ordered.sort()
    data_ordered = data_ordered[np.searchsorted(data_ordered, -32766):]

    (means, iters, average_x) = cluster_fast_dataset(data_ordered, k)

    # We now have the final clustering - display the means of each cluster!
    if DEBUG:
        print(means)
        print(iters)
        print(average_x)

    # For each data point, find its cluster and make the value of the data point equal to the mean of the cluster.
    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] is None:
                continue
            cluster = closest_search_naive(data[i][j], means)
            data[i][j] = means[cluster]

    # Since data is ordered, we can get min/max like this
    min = data_ordered[0]
    max = data_ordered[len(data_ordered)-1]

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
        data[variable], min, max = fcluster(data[variable], k)
        ranges[variable] = (min, max)

    # Now write this to a new data json so it can be mapped.
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
    output_dir = f"{FCLUSTERED_DIRECTORY}/{args.output}" if args.output else FCLUSTERED_DIRECTORY

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
