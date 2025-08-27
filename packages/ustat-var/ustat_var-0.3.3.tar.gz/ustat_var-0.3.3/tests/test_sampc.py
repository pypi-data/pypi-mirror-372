# Dependencies
import numpy as np
import numpy.ma as ma
import pytest
from ustat_var.sampc import sampc


def test_sampc_simple():
    '''Test the sampc helper function on a simple case'''
    
    # Test arrays
    X = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ])
    Y = np.array([
        [1.0, 2.0, 3.0],
        [6.0, 5.0, 4.0]
    ])
    
    # Sampc() should return rowwise sampling covariance between X and Y
    expected = [np.cov(X[row,:], Y[row,:])[0,1] for row in range(X.shape[0])]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)


def test_sampc_some_nans():
    '''Test the sampc helper function on a simple case with some NaNs'''
    
    # Test arrays
    X = np.array([
        [1.0, np.nan, 3.0],
        [4.0, 5.0, np.nan]
    ])
    Y = np.array([
        [2.0, np.nan, 6.0],
        [6.0, 5.0, np.nan]
    ])
    
    # Sampc() should return rowwise sampling covariance between X and Y
    expected = [ma.cov(ma.masked_invalid(X[row,:]), ma.masked_invalid(Y[row,:]))[0,1] for row in range(X.shape[0])]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)
    

def test_sampc_no_valid_pairs():
    '''Test the sampc helper function on a simple case with some NaNs'''
    
    # Test arrays
    X = np.array([
        [1.0, np.nan, 3.0, np.nan],
        [np.nan, 3.0, np.nan, 1.0]
    ])
    Y = np.array([
        [np.nan, 4.0, np.nan, 8.0],
        [8.0, np.nan, 4.0, np.nan]
    ])
    
    # Expect to return all 0s when no valid pairs.
    expected = [0,0]
    result = sampc(X,Y)
    
    # Test within tolerance
    np.testing.assert_allclose(result, expected, rtol=1e-6)