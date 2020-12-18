from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import argparse
import errno
import json
from random import randint
import multiprocessing as mp
import numpy as np
from consts import TOTAL_LAT, TOTAL_LON, VARIABLES, CONVERTED_DIRECTORY, FCLUSTERED_DIRECTORY

DEBUG = False
JSON_FILENAME = 'converted_data.json'


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
        # Take the old divider location between cluster[i] and cluster[i+1].
        # Is it in the same place, further to the left or to the right?
        # If it's in the same place, then datapoints[dividerpos-1] < cluster_inbetweens[i] and datapoints[dividerpos] > cluster_inbetweens[i].
        #print(f"data[divide[i]-1]: {datapoints[dividerpos[i]-1]}, cluster_inbetween[i]: {cluster_inbetweens[i]}, data[divide[i]]: {datapoints[dividerpos[i]]}")
        if datapoints[dividerpos[i]-1] < cluster_inbetweens[i] and datapoints[dividerpos[i]] >= cluster_inbetweens[i]:
            #print("Divider is in the same place. Rejoice! Do nothing.")
            continue

        # If it's to the left, then datapoints[dividerpos-1] >= cluster_inbetweens[i]
        # If it's to the right, then 
        if datapoints[dividerpos[i]-1] >= cluster_inbetweens[i]:
            #print("It's to the left!")

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
        else:
            #print("It's to the right!")
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

            # j is the new divider position. We don't need to store it though so it's fine.
            dividerpos[i] = j

    return (cluster_sums, cluster_count, n / (k-1))


def cluster_fast_dataset(dataset, cluster_count):
    """
    cluster_fast_dataset

    parameters:
     - dataset : dataset to cluster
     - cluster_count : TODO till in 

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
            x_sum += x + 1
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
    return (new_means, iters, x_sum / iters)


def fcluster(data):
    # 1: Choose k random points, assign the mean of each cluster to the value of its single data point
    # 2: Assign each data point its cluster based on which mean is closest
    # 3: Calculate the new means for each cluster based on the data points inside
    # 4: If the new means are different than the previous means, repeat from step 2

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

    (means, iters, average_x) = cluster_fast_dataset(data_ordered, 25)

    # We now have the final clustering - display the means of each cluster!
    # print(means)
    # print(iters)
    # print(average_x)

    # For each data point, find its cluster and make the value of the data point equal to the mean of the cluster.
    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] is None:
                continue
            cluster = closest_search_naive(data[i][j], means)
            data[i][j] = means[cluster]
    return data


def cluster_file(filename):
    print('fclustering', filename)

    with open(filename, 'r') as my_file:
        data = json.load(my_file)

    for variable in VARIABLES:
        data[variable] = fcluster(data[variable])

    # variable = VARIABLES[0]
    # data[variable] = fcluster(data[variable])

    # Now write this to a new data json so it can be mapped.
    with open(f"{FCLUSTERED_DIRECTORY}/{basename(filename)}", 'w') as outfile:
        json.dump(data, outfile)


def init():
    try:
        makedirs(FCLUSTERED_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input JSON file')
    args = parser.parse_args()

    init()

    if args.input and isfile(args.input):
        print('Cluster', args.input)
        cluster_file(args.input)

    elif args.input and isdir(args.input):
        print('Cluster files in', args.input)
        files = [f"{args.input}/{f}" for f in listdir(args.input) if isfile(join(args.input, f))]

        pool = mp.Pool(mp.cpu_count())
        pool.map(cluster_file, files)

    else:
        print('Cluster files in', CONVERTED_DIRECTORY)
        files = [f"{CONVERTED_DIRECTORY}/{f}" for f in listdir(CONVERTED_DIRECTORY) if isfile(join(CONVERTED_DIRECTORY, f))]
        pool = mp.Pool(mp.cpu_count())
        pool.map(cluster_file, files)
