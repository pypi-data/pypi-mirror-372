import numpy as np
import cython
cimport numpy as cnp


@cython.wraparound(False)
@cython.boundscheck(False)
def _getresults(cnp.ndarray array,cnp.ndarray time_diff, int multi, int cycle1, start, int ix):
    cdef int index = 0
    #cdef cnp.ndarray result = np.array([])
    #cdef cnp.ndarray first_data
    #cdef cnp.ndarray values
    cdef cython.bint fr = not bool(ix)
    cdef int size = array.shape[0]
    cdef Py_ssize_t j

    if not fr:
        first_data = array[:ix, :]
        result =  [start, first_data[:, 1][0], first_data[:, 2].max(
        ), first_data[:, 3].min(), first_data[:, 4][-1], first_data[:, 5].sum()]
        array = array[ix:, :]
        time_diff = time_diff[ix:]
        fr = False

    for j in range(multi, size):
        if j % multi == 0 or time_diff[j] != cycle1:
            length = j-index
            index = j
            values = array[j-length:j]
            if fr:
                result =  [values[:, 0][0], values[:, 1][0], values[:, 2].max(
                ), values[:, 3].min(), values[:, 4][-1], values[:, 5].sum()]
                fr = False
            result = np.row_stack((result, [values[:, 0][0], values[:, 1][0], values[:, 2].max(
            ), values[:, 3].min(), values[:, 4][-1], values[:, 5].sum()]))
    else:
        if index != j:
            values = array[index:]
            result = np.row_stack((result, [values[:, 0][0], values[:, 1][0], values[:, 2].max(
            ), values[:, 3].min(), values[:, 4][-1], values[:, 5].sum()]))
    return result
