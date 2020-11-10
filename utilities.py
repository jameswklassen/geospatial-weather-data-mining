# Gets all observations of a variable belonging to the provided cast
# cast: The cast to get observation information from
# variable: The dataset variable with the desired observations.
# variable_row_size: The array containing the number of observations per cast
# for this variable.
def get_cast_obs(cast, variable, variable_row_size):
    start_index = 0

    for i in range(0, cast):
        start_index = start_index + variable_row_size[i]

    end_index = start_index + variable_row_size[cast]
    return variable[start_index:end_index]
