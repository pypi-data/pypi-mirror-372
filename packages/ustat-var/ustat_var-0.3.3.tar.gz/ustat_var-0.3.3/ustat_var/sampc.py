# Dependencies
import numpy as np

# Helper function for sampling covariances
def sampc(X,Y):
    r'''
    Computes the sampling covariance between rows of J-by-:math:`\operatorname{max}(T_j)` arrays X and Y.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals for outcome X
    Y: array 
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals for outcome X

    Returns
    -------
    array
        J-by-1 array containing sampling covariance between each row of X and Y.
    '''
    Xmeans = np.nanmean(X, axis=1)
    Ymeans = np.nanmean(Y, axis=1)
    XYcounts = np.array(np.sum(~np.isnan(X) & ~np.isnan(Y), axis=1),dtype=float)
    XYcovar = np.nansum((X-Xmeans[:,np.newaxis])*(Y-Ymeans[:,np.newaxis]),1,dtype=float)/(XYcounts-1)
    XYcovar[XYcounts <= 1] = 0  
    return XYcovar
