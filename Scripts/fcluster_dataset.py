import numpy as np
import json
import multiprocessing as mp
from random import randint
from consts import TOTAL_LAT, TOTAL_LON, VARIABLES

JSON_FILENAME = 'converted_data.json'
k = 25

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

def closest_search_no_dups(datapoints, k, means, cluster_sums, cluster_count):
    # This method takes in ALL datapoints (sorted as a numpy array),
    # the means, sums and counts for all clusters,
    # and updates clustermeans, clustersums and clustercounts.

    # Find all cluster positions - O(k)
    cluster_sums = cluster_sums.copy()
    cluster_count = cluster_count.copy()

    #print("hello :) in algorithm")
    dividerpos = [0]*(k-1)

    dividerpos[0] = cluster_count[0]
    
    for i in range(1, k-1):
        dividerpos[i] = dividerpos[i-1] + cluster_count[i]

    # Step 1: Find the average between every two adjacent cluster means - O(k)
    cluster_inbetweens = [0]*(k-1)
    for i in range(k-1):
        cluster_inbetweens[i] = (means[i]+means[i+1])/2
    
    #print(f"dividerpos: {dividerpos}")
    #print(f"inbetweens: {cluster_inbetweens}")
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

    #print("Algorithm done!")
    #print(f"dividerpos: {dividerpos}")
    #print(f"cluster_sums: {cluster_sums}")
    #print(f"cluster_count: {cluster_count}")
    print(n/k)
    return (cluster_sums, cluster_count, n/k)

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
    
    cluster_sums = [0]*k
    cluster_count = [0]*k

    # Use O(n log n) time to determine cluster sums and cluster counts
    data_ordered = np.zeros(TOTAL_LAT * TOTAL_LON)
    data_ordered.fill(-32767)

    for i in range(TOTAL_LAT):
        for j in range(TOTAL_LON):
            if data[i][j] is not None:
                data_ordered[i*TOTAL_LON+j] = data[i][j]
    
    data_ordered.sort()
    data_ordered = data_ordered[np.searchsorted(data_ordered, -32766):]
    print(len(data_ordered))
    
    # NOTE: Randomly choosing data points has a chance of creating clusters with 0 items in it which will crash the program.
    for i in range(k):
        x = None
        while x is None:
            x = data_ordered[randint(0, len(data_ordered))]
        new_means[i] = x
    
    # Determine the min/max of the data points
    #minimum = 99999999
    #maximum = -9999999

    #for i in range(TOTAL_LAT):
    #    for j in range(TOTAL_LON):
    #        if data[i][j] is None:
    #            continue

    #        if data[i][j] < minimum:
    #            minimum = data[i][j]
    #        elif data[i][j] > maximum:
    #            maximum = data[i][j]
    
    # We now have minimum and maximum. Evenly divide the new means.
    #for i in range(k):
    #    new_means[i] = (i/k)*minimum + (1-i/k)*maximum # Simple linear interpolation

    # Sort means by magnitude
    new_means.sort()
    print(new_means)


    
    # Get rid of any None values

    # Determine cluster sums and cluster counts
    dividing_points = [0]*(k-1)
    for i in range(k-1):
        dividing_points[i] = (new_means[i] + new_means[i+1])/2
    
    current_dividing_point = 0

    for i in range(len(data_ordered)):
        if current_dividing_point < k-1 and data_ordered[i] >= dividing_points[current_dividing_point]:
            current_dividing_point += 1
            print(f"dividing at {i}")
        cluster_count[current_dividing_point] += 1
        cluster_sums[current_dividing_point] += data_ordered[i]
        

    print(cluster_count)
    print(cluster_sums)

    print("Starting loop")
    iters = 0
    while not np.array_equal(means, new_means):
        iters += 1
        means = new_means.copy()
        new_means = np.zeros(k)
        
        # 2: Assign each value to whichever mean is closest (random tiebreaker)
        # Are there any duplicates in the means?
        if not np.array_equal(means, np.unique(means)):
            print("Slow method")
            # There is, so let's use the old slow method instead.
            cluster_sums = [0]*k
            cluster_count = [0]*k
            for i in range(TOTAL_LAT):
                for j in range(TOTAL_LON):
                    if data[i][j] == None:
                        continue
                    cluster = closest_search(data[i][j], means)
                    cluster_sums[cluster] += data[i][j]
                    cluster_count[cluster] += 1
        else:
            # There isn't! Gotta go fast!
            (cluster_sums, cluster_count) = closest_search_no_dups(
                data_ordered, k, means, cluster_sums, cluster_count
            )

        #print(cluster_count)

        # 3: Calculate new cluster means
        for i in range(k):
            new_means[i] = cluster_sums[i]/cluster_count[i]

        # Due to the way the algorithm works, the new means can never go out of order.
        # new_means.sort()
        
        # 4: If means are different than new means, go back to 2
    
    # We now have the final clustering - display the means of each cluster!
    print(new_means)
    print(iters)
    # For each data point, find its cluster and make the value of the data point equal to the mean of the cluster.
    #for i in range(TOTAL_LAT):
    #    for j in range(TOTAL_LON):
    #        if data[i][j] == None:
    #            continue
    #        cluster = closest_search(data[i][j], new_means)
    #        full_data[VARIABLES[4]][i][j] = new_means[cluster]
    
    # Now write this to a new data json so it can be mapped.
    #with open('converted_data2.json', 'w') as outfile:
    #    json.dump(full_data, outfile)