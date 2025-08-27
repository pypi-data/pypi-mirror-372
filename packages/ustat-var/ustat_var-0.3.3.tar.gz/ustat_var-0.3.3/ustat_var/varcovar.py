# Dependencies:
import numpy as np
from scipy import sparse

# U-stat estimator of variance / covariance
def varcovar(origX, origY, w=None, quiet=True):
    r'''
    U-stat estimator of variance / covariance for teacher effects
    X and Y are a J-by-:math:`\operatorname{max}(T_j)` matrix of teacher-specific mean residuals. 
    When X and Y are residuals for the same outcome and covariate group,
    code will return a estimate of variance of teacher effects. When X and Y
    differ (either in outcome or Xs), code returns an estimate of the 
    covariance. 

    Each row of X and Y are residuals for a specific teacher, ordered as
    first year observed, second year observed, etc. Since teachers have
    different number of years observed, X and Y should be np.NaN for all
    years after the last year observed. Each teacher must have at least
    2 years observed.

    X and Y must have the same dimension.
    
    Parameters
    ----------
    origX: array
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals/data for outcome X
    origY: array
        J-by-:math:`\operatorname{max}(T_j)` array containing residuals/data for outcome Y
    w: array
        (Optional) J-by-1 array of user-supplied weights. If supplied, varcovar will return row-weighted variance-covariance of row means. 
    quiet: boolean
        (Optional) If quiet=True, function call will report type of variance being calculated (unweighted/weighted) and whether panels are balanced or unbalanced.

    Returns
    -------
    float
        Variance-covariance between rowmeans of origX and origY.

    '''
    
    ## 1 Input checks ##
    # Check if X, Y have observations
    if (len(origX) == 0) | (len(origY) == 0):
        print('No observations in X or Y matrices')
        return np.nan
    
    # Check if user supplied weights.
    # If they exist, describe what type of weights they are
    if not(w is None):
        weights = w
        if (weights.ndim != 1):
            ValueError("Supplied weights have strange dimension. The 'w' object needs to be an array with J elements, where J is the number of rows in A and B. Inspect and retry.")
    
    # Function does not support X_{jt} = 0 (since these are indistinguishable from NaN/missing values).
    # Raise error if 0 value detected.
    if (np.sum(origX == 0) != 0) | (np.sum(origY == 0) != 0):
        raise ValueError("Supplied data has at least 1 data point which =0. 0 data points are not supported. Please inspect and try again.")
    
    
    ## 2 Compute necessary values ## 
    # Counds of valid obs
    countsX = np.count_nonzero(~np.isnan(origX),1)  # No. of obs in X
    countsY = np.count_nonzero(~np.isnan(origY),1)  # No. of obs in Y
    nsquares = np.count_nonzero(~np.isnan(origX * origY),1)   # No. of obs in both X and Y
    nproducts = (countsX*countsY - nsquares) # No. of valid product pairs
    X = np.nan_to_num(origX[nproducts > 0, :].copy(), 0) # Create X, which is copy of origX, though removing teachers who only have 1 observation on a specific outcome.
    Y = np.nan_to_num(origY[nproducts > 0, :].copy(), 0) # Same for Y and origY here. In  both, we replace NaNs with 0. 
    

    ## 3 Reporting ##
    # Report what type of variance calculation is being implemented.
    if (w is None):
        calc_type = "unweighted"
        
    elif not(w is None):
        calc_type = "weighting by rows"
    
    # Report whether panels are balanced/unbalanced
    check_balance = np.sum((np.isnan(origX) == np.isnan(origY)).all())
    if check_balance == 1:
        panel_type = "balanced within-teacher"
    else:
        panel_type = "unbalanced within- and between-teachers"
    
    # Tell user type of calculation/observed panel type
    if not(quiet):
        report_message = "Panels are \033[1m" + panel_type + "\033[0m \n Calculating variance by \033[1m" + calc_type + "\033[0m..."
        print(report_message)
    
    ## 4 Calculation ##
    
    # 4.1 Calculate second term
    
    if not(w is None):
        # User-supplied teacher weights option.
        
        # Computed unweighted teacher means Mu
        X_means = np.nanmean(origX[nproducts > 0, :], 1)
        Y_means = np.nanmean(origY[nproducts > 0, :], 1)
        
        # Weight Mu by teacher weights
        X_means = (weights / np.nansum(weights)) * X_means 
        Y_means = (weights / np.nansum(weights)) * Y_means
        
        # Take products, remove j = k case, and sum up
        tmp = X_means.reshape(-1,1).dot(Y_means.reshape(1,-1))
        np.fill_diagonal(tmp,0)
        gmean = np.sum(tmp)
        
    else:
        # Unweighted option
        
        # Unweighted teacher mean
        X_means = np.nanmean(origX[nproducts > 0, :],1) 
        Y_means = np.nanmean(origY[nproducts > 0, :],1)
        
        # Take products, removing j = k case and sum up
        tmp = X_means.reshape(-1,1).dot(Y_means.reshape(1,-1)) # Take X_means' %*% Y_means.
        np.fill_diagonal(tmp,0)
        gmean = np.sum(tmp) / (len(X_means)*len(Y_means)) 


    # 4.2 Calculate first term
    # Diagonalizied sparse matrix for taking products (columns of diag X will replicate a row of X, with the remaining elements in the column being 0)
    diagX = sparse.csr_matrix(
            (X.ravel(),
            (np.arange(X.shape[0]*X.shape[1]),
            np.repeat(np.arange(X.shape[0]),X.shape[1]))
            ))

    # Generate all teacher-year product pairs (The resulting product will have the mean teacher residual in time t from X multiplied by the mean teacher residual in time t from Y.
    k = diagX.dot(sparse.csr_matrix(Y))
    
    # Create matrix to help take sums within teacher of the 'k' matrix.
    teach_sum = sparse.csr_matrix(
            (np.ones(X.shape[0]*X.shape[1]),
                (np.arange(X.shape[0]*X.shape[1]),
                np.repeat(np.arange(X.shape[0]),X.shape[1]))
                ))
    
    # This multiplication sums up the products for each teacher, which will yield the total sum of the product of mean residuals across all pairs of years.
    sums = teach_sum.T.dot(np.sum(k,1))
    sums = (sums - np.nansum(X * Y, 1)[:,np.newaxis]) # Subtract the t=t product pairs.
    
    # Divide by no. of teacher-year product pairs
    sums = sums.ravel()/nproducts[nproducts > 0]
    
    
    # Calculate appropriate mean of means
    if not(w is None):
        # Weighted variance option
        w_norm = weights / np.sum(weights)
        _weights = w_norm * (1 - w_norm)
        sums = np.array(sums) * np.array(_weights)
        Ustat = np.sum(sums) - gmean
        
    else:
        # Unweighted option
        Ustat = (len(X_means)-1)/len(X_means)*np.mean(sums) - gmean
    
    
    ## 5 Return sampling vairance estimate ##
    return Ustat
    

    
