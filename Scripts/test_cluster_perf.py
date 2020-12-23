import numpy as np
import multiprocessing as mp
from fcluster import cluster_fast_dataset


def main():
    """
    Test how the average x value changes depending on the characteristics of the dataset.

    Characteristics to test:
        - Uniform distribution
        - Normal distribution
        - Several normal distributions overlayed
        - Exponential distribution (e^uniform)
    """

    # We also want to test how the average x value scales with the size of the dataset.
    # We want to use this data to do an empirical analysis on the runtime of this new algorithm.

    iterations_per_core = 2
    min_size = 10000
    max_size = 1000001
    step_size = 10000
    min_k = 5
    mid_k = 25
    max_k = 1000
    k_step = 5

    do_uniform_tests(iterations_per_core, min_size, mid_k)
    do_normal_tests(iterations_per_core, min_size, mid_k)
    do_overlap_tests(iterations_per_core, min_size, mid_k)

    # do_uniform_tests(iterations_per_core, max_size, mid_k)
    # do_normal_tests(iterations_per_core, max_size, mid_k)
    # do_overlap_tests(iterations_per_core, max_size, mid_k)

    do_scale_n_tests(iterations_per_core, min_size, max_size, step_size, mid_k)


def get_uniform_distribution(size, start, end):
    return np.random.uniform(start, end, size)


def get_normal_distribution(size, mid, stddev):
    return np.random.normal(mid, stddev, size)


def get_overlap_distribution(size_each, mids, stddev):
    return np.concatenate([np.random.normal(mid, stddev, size_each) for mid in mids])


def do_uniform_tests(iterations, size, k):
    """
    Gather information on the average x value over a uniform distribution

    parameters:
        - iterations : number of iterations
        - size : size of the uniform distribution
    """

    start = 0
    end = 10000
    result = do_n_tests_parallel(iterations, get_uniform_distribution, k, size, start, end)

    print(f"The average x value for a uniform distribution starting at {start} and ending at {end} with size {size} is approximately {result}")


def do_normal_tests(iterations, size, k):
    """
    Gather information on the average x value over a normal distribution

    parameters:
        - iterations : number of iterations
        - size : size of the normal distribution
    """

    mid = 2000
    stddev = 500
    result = do_n_tests_parallel(iterations, get_normal_distribution, k, size, mid, stddev)

    print(f"The average x value for a normal distribution with mid {mid} and std. deviation {stddev} with size {size} is approximately {result}")


def do_overlap_tests(iterations, size, k):
    """
    Gather information on the average x value over a overlapped normal distribution

    parameters:
        - iterations : number of iterations
        - size : size of the overlapped normal distribution
    """

    mids = [200, 800, 1200, 1500]
    stddev = 150
    result = do_n_tests_parallel(iterations, get_overlap_distribution, k, size // len(mids), mids, stddev)

    print(f"The average x value for a set of overlapped normal distributions with mids {mids} and std. deviation {stddev} with size {size} is approximately {result}")


def do_scale_n_tests(iterations_each, min_size, max_size, step_size, k):
    # Use an overlap normal distribution since that seems to have the highest average x-value

    start = 0
    end = 10000000
    x_avgs = [0]*len(range(min_size, max_size, step_size))
    iteration = 0

    for size in range(min_size, max_size, step_size):
        result = do_n_tests_parallel(iterations_each, get_uniform_distribution, k, size, start, end)

        x_avgs[iteration] = result
        print(f"{size}: {x_avgs[iteration]}")
        iteration += 1

    print(x_avgs)


def do_n_tests_parallel(iterations_per_core, method, k, *args):
    num_cores = mp.cpu_count()

    datasets = [[method(*args) for _ in range(iterations_per_core)] for _ in range(num_cores)]

    # Run in parallel
    pool = mp.Pool(num_cores)
    results = pool.starmap(do_n_tests_bootstrap, [(iterations_per_core, k, datasets[i]) for i in range(num_cores)])

    return np.mean(results)


def do_n_tests_bootstrap(n, k, datasets):
    x_sum = 0
    iter_sum = 0
    for dataset in datasets:
        (_, iters, x_avg) = cluster_fast_dataset(dataset, k)
        x_sum += x_avg
        iter_sum += iters

    return x_sum / n


if __name__ == '__main__':
    main()
