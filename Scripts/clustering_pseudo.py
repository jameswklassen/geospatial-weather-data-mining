# Partitioning/Clustering Algorithm

# First choose a variable from the dataset that we want to use for mining

sea_surface_temperature = ctd.variables['sst']

# Algorithm

n = len(sea_surface_temperature)  # the number of data points in the dataset for our chosen variable
k = 6  # the chosen number of max desired partitions where k <= n
k_curr = 2  # current number of partitions starts at 2
k_means[2]  # set of k-means for each partition
k_partitions[2]  # set of tuples that are the start and end indexes of each partition

# Define the index ranges of each partition

partition_size = n / k_curr

for i in range(0, k_curr):
    k_start_index = i * partition_size
    k_end_index = partition_size * (i + 1)
    k_partitions[i] = (k_start_index, k_end_index)


# Calculate k-mean for each partition
for i in range(0, k_curr):
    k_means[i] = mean(k_partitions[i])

# calculate the distances

k_distances[k_curr][n]

for i in range(0, k_curr):
    for j in range(0, n):
        k_distances[i][j] = abs(k_means[i] - sst[j])

# now all dinstances for every point to every k_mean is calculated
# now do the partitioning
# how to actually assign the values to a different partition?