import numpy as np
import json
import multiprocessing as mp
import argparse
import math
from random import randint

from fcluster_dataset import cluster_fast_dataset


def main():
    # We want to test how the average x value changes depending on the characteristics of the dataset.
    # Characteristics to test:
    # - Uniform distribution
    # - Normal distribution
    # - Several normal distributions overlayed
    # - Exponential distribution (e^uniform)

    # We also want to test how the average x value scales with the number of clusters and also the size of the dataset.
    # We want to use this data to do an empirical analysis on the runtime of this new algorithm.

    iterations = 100
    min_size = 970000
    max_size = 1000001
    step_size = 10000
    min_k = 5
    mid_k = 25
    max_k = 1000
    k_step = 5

    #do_uniform_tests(iterations, min_size, mid_k)
    #do_normal_tests(iterations, min_size, mid_k)
    #do_overlap_tests(iterations, min_size, mid_k)
    #do_exponential_tests(iterations, min_size, mid_k)

    do_scale_n_tests(26, min_size, max_size, step_size, mid_k)
    do_scale_k_tests(iterations, min_k, max_k, max_size)


def get_uniform_distribution(size, start, end):
    return np.random.uniform(start, end, size)

def get_normal_distribution(size, mid, stddev):
    return np.random.normal(mid, stddev, size)

def get_overlap_distribution(size_each, mids, stddev):
    return np.concatenate([np.random.normal(mid, stddev, size_each) for mid in mids])

def get_exponential_distribution(size, start, end):
    return math.e**get_normal_distribution(size, start, end)


def do_uniform_tests(iterations, size, k):
    # Gather information on the average x value for a uniform distribution of the given size,
    # over a specified number of iterations

    x_sum = 0
    start = 0
    end = 10000
    for i in range(iterations):
        if i % 25 == 0:
            print(i)

        dataset = get_uniform_distribution(size, start, end)

        (_, _, x_avg) = cluster_fast_dataset(dataset, k)
        x_sum += x_avg
    
    print(f"The average x value for a uniform distribution starting at {start} and ending at {end} with size {size} is approximately {x_sum/iterations}")


def do_normal_tests(iterations, size, k):
    # Gather information on the average x value for a normal distribution of the given size,
    # over a specified number of iterations

    x_sum = 0
    mid = 2000
    stddev = 500
    for i in range(iterations):
        if i % 25 == 0:
            print(i)

        dataset = get_normal_distribution(size, mid, stddev)

        (_, _, x_avg) = cluster_fast_dataset(dataset, k)
        x_sum += x_avg
    
    print(f"The average x value for a normal distribution with mid {mid} and std. deviation {stddev} with size {size} is approximately {x_sum/iterations}")


def do_overlap_tests(iterations, size, k):
    # Gather information on the average x value for a overlapped normal distribution of the given size,
    # over a specified number of iterations

    x_sum = 0
    mids = [200, 8000, 1100, 1500]
    stddev = 150
    for i in range(iterations):
        if i % 25 == 0:
            print(i)

        dataset = get_overlap_distribution(size // len(mids), mids, stddev)

        (_, _, x_avg) = cluster_fast_dataset(dataset, k)
        x_sum += x_avg

    print(f"The average x value for a set of overlapped normal distributions with mids {mids} and std. deviation {stddev} with size {size} is approximately {x_sum/iterations}")


def do_exponential_tests(iterations, size, k):
    # Gather information on the average x value for a exponential distribution of the given size,
    # over a specified number of iterations

    x_sum = 0
    start = -5
    end = 12
    for i in range(iterations):
        if i % 25 == 0:
            print(i)
        
        dataset = get_exponential_distribution(size, start, end)

        (_, _, x_avg) = cluster_fast_dataset(dataset, k)
        x_sum += x_avg
    
    print(f"The average x value for an exponential distribution with start exponent {start} and end exponent {end} with size {size} is approximately {x_sum / iterations}")



def do_scale_n_tests(iterations_each, min_size, max_size, step_size, k):
    # Use an overlap normal distribution since that seems to have the highest average x-value
    #mids = [200, 8000, 1100, 1500]
    mid = 10000
    stddev = 1000
    x_avgs = [0]*len(range(min_size, max_size, step_size))
    iteration = 0

    for size in range(min_size, max_size, step_size):
        x_sum = 0

        for i in range(iterations_each):
            dataset = get_uniform_distribution(size, 0, 10000000)

            (_, _, x_avg) = cluster_fast_dataset(dataset, k)
            x_sum += x_avg
        
        x_avgs[iteration] = x_sum / iterations_each
        print(f"{size}: {x_avgs[iteration]}")
        iteration += 1
    
    #print(f"The following is an array of average x values for the overlapped normal distribution with mids {mids} and standard deviation {stddev}")
    #print(f"The size of each dataset starts at {min_size} and ends at {max_size} in increments of {step_size}")
    print(x_avgs)
        



def do_scale_k_tests(iterations_each, min_k, max_k, size):
    pass


if __name__ == '__main__':
    main()
