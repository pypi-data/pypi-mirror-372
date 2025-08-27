"""
Helper functions for generating test data arrays with or without NaN patterns,
primarily used to test unbiased variance and covariance estimators.
"""

# Dependencies
import numpy as np

# Functions
def generate_unique_nan_arrays(n_rows, n_cols, n_arrays, nan_prob, min_int, max_int, balanced=False, seed=None):
    r"""
    Generates unique arrays with either balanced or unbalanced NaN patterns. Each element will be a random integer.

    Parameters
    ----------
    n_rows: int
        Number of rows in each array.
    n_cols: int
        Number of columns in each array.
    n_arrays: int
        Number of arrays to generate.
    nan_prob: float
        Probability of a NaN per element (when unbalanced, applies once for all arrays. See balanced argument).
    min_int: int
        Minimum integer for random number generation.
    max_int: int
        Maximum integer for random number generation.
    balanced: boolean
        If True, all arrays share the same NaN pattern but have different values otherwise.
    seed: int
        Optional random seed.

    Returns
    -------
    list of ndarray
        Arrays with random numbers and NaN elements.
    """
    if seed is not None:
        np.random.seed(seed)

    arrays = []

    if balanced:
        # Generate shared NaN mask
        nan_mask = np.random.rand(n_rows, n_cols) < nan_prob
        for _ in range(n_arrays):
            arr = np.random.randint(min_int, max_int, size=(n_rows, n_cols)).astype(float)
            arr[nan_mask] = np.nan
            arrays.append(arr)

    else:
        # Unbalanced: generate unique masks per array per row, as before
        nan_masks = []
        for i in range(n_arrays):
            arr = np.random.randint(min_int, max_int, size=(n_rows, n_cols)).astype(float)
            arrays.append(arr)
            nan_masks.append(np.full((n_rows, n_cols), False))

        for row in range(n_rows):
            used_masks = set()
            for arr_idx in range(n_arrays):
                while True:
                    mask = np.random.rand(n_cols) < nan_prob
                    mask_tuple = tuple(mask)
                    if mask_tuple not in used_masks:
                        used_masks.add(mask_tuple)
                        nan_masks[arr_idx][row] = mask
                        break

        for i in range(n_arrays):
            arrays[i][nan_masks[i]] = np.nan

    return arrays



import numpy as np

def generate_data(n_teachers, n_time, n_arrays, var_fixed=1.0, var_noise=1.0, cov_factor=0.5, seed=None):
    """
    Generates n_arrays arrays of size (n_teachers, n_time), all with fixed variance and covariance structure.

    Parameters
    ----------
    n_teachers : int
        Number of rows (teachers).
    n_time : int
        Number of columns (time periods).
    n_arrays : int
        Number of arrays to generate.
    var_fixed : float
        Desired variance for elements.
    var_noise : float
        Variance of added noise.
    cov_factor : float
        Factor controlling covariance between arrays.
    seed : int, optional
        Optional random seed.

    Returns
    -------
    list of ndarray
        Arrays with fixed variance/covariance.
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Random mean vector (n_teachers x 1)
    mu = np.random.normal(loc=0, scale=np.sqrt(var_fixed), size=(n_teachers, 1))
    
    # Base matrix A using mu and fixed variance
    A = np.random.normal(loc=mu, scale=np.sqrt(var_noise), size=(n_teachers, n_time))
    
    # Set up array storage and append A
    arrays = []
    arrays.append(A)
    
    # Generate new arrays
    for _ in range(n_arrays-1):
        # Generate noise with covariance control
        _mu = mu * cov_factor
        new_array = np.random.normal(loc=_mu, scale=np.sqrt(var_noise), size=(n_teachers, n_time))
        arrays.append(new_array)

    return arrays

