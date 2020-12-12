import numpy as np
import json
import multiprocessing as mp
from random import randint
from consts import TOTAL_LAT, TOTAL_LON, VARIABLES

JSON_FILENAME = 'converted_data.json'
k = 2

# This function breaks ties in the case of there being clusters with identical means.
def choose_random_duplicate(clustermeans, index, backwards):
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


if __name__ == '__main__':
    # Open our converted data and read it in
    with open(JSON_FILENAME, 'r') as my_file:
        full_data = json.load(my_file)
    
    # 1: Choose k random points, assign the mean of each cluster to the value of its single data point
    # 2: Assign each data point its cluster based on which mean is closest
    # 3: Calculate the new means for each cluster based on the data points inside
    # 4: If the new means are different than the previous means, repeat from step 2

    # 1: Choose k random points (sea surface temperature)
    data = full_data[VARIABLES[4]]
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
    print(new_means)

    while not np.array_equal(means, new_means):
        means = new_means.copy()
        new_means = np.zeros(k)

        # 2: Assign each value to whichever mean is closest (random tiebreaker)
        for i in range(TOTAL_LAT):
            for j in range(TOTAL_LON):
                if data[i][j] == None:
                    continue
                cluster = closest_search(data[i][j], means)
                cluster_points[cluster][cluster_count[cluster]] = data[i][j]
                cluster_count[cluster] += 1

        print(cluster_count)

        # 3: Calculate new cluster means
        for i in range(k):
            new_means[i] = np.resize(cluster_points[i], cluster_count[i]).mean()

            # Reset cluster count to prevent bad things
            cluster_count[i] = 0
        
        new_means.sort()
        
        # 4: If means are different than new means, go back to 2
    
    # We now have the final clustering - display the means of each cluster!
    print(new_means)

    # For each data point, find its cluster and make the value of the data point equal to the mean of the cluster.
    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] == None:
                continue
            cluster = closest_search(data[i][j], new_means)
            full_data[VARIABLES[4]][i][j] = new_means[cluster]
    
    # Now write this to a new data json so it can be mapped.
    with open('converted_data2.json', 'w') as outfile:
        json.dump(full_data, outfile)