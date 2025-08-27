# Dependencies
import numpy as np

# Helper for C functions, general case when X != Y
def makec(X,Y, w=None):
    r"""
    Generates C-weights for U-statistic estimator.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    Y: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome Y.
    w: array
        J-by-1 array containing row-wise/teacher-level weights (optional).

    Returns
    -------
    list of ndarray
        First array contains C-weights for specific teachers (i.e. weight when :math:`j(i) = j(k)`), and second element contains array of cross-term C-weights (i.e. weight when :math:`j(i) \neq j(k)`)
    
    """  
    
    # Number of observations in X, Y, and intersection
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float) # returns no. of observations across all teachers in X (e.g. event X)
    Ycounts = np.array(np.sum(~np.isnan(Y), axis=1),dtype=float) # returns no. of observations across all teachers in Y (e.g. event Y)
    XYcounts = np.array(np.sum(~np.isnan(X) & ~np.isnan(Y), axis=1),dtype=float) # returns no. of observations across all teachers in XandY (e.g. shared observations)
    J = sum(Xcounts*Ycounts - XYcounts > 0) 
    
    # Check if weights are teacher-level and that each valid teacher has a weight.
    # Fail if not.
    if not(w is None):
        if (w.ndim != 1):
            raise ValueError("Weight object has wrong dimension. You need to supply teacher-level weights only (i.e. 1 weight per teacher). Check 'w' and try again.")
        elif (len(w) != J):
            raise ValueError("Not enough weights supplied (i.e. some teachers didn't receive weights). Check 'w' and try again.")
        
    # Compute C coefficients
    if (w is None):
        # Unweighted (each teacher receives equal weight
    
        C_jj = (J-1)/J**2/(Xcounts*Ycounts - XYcounts)
        C_jj[(Xcounts*Ycounts - XYcounts) == 0] = 0
        C_jk = -1/J**2*(1/Xcounts).reshape(-1,1).dot((1/Ycounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Ycounts == 0] = 0
    
    else:
        # Weighted (each teacher receives weight corresponding to entries in w)
        w_norm = w / np.sum(w) # Normalised weights
        
        C_jj = w_norm * (1 - w_norm) * (1/(Xcounts*Ycounts - XYcounts))
        C_jj[(Xcounts*Ycounts - XYcounts) == 0] = 0
        C_jk = -(w_norm * w_norm)*(1/Xcounts).reshape(-1,1).dot((1/Ycounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Ycounts == 0] = 0
    

    return C_jj, C_jk



# C weights when X = Y
def makec_spec(X, w=None):
    r"""
    Generates C-weights for U-statistic estimator in special case when X = Y. 

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    w: array
        J-by-1 array containing row-wise/teacher-level weights (optional).

    Returns
    -------
    list of ndarray
        First array contains C-weights for specific teachers (i.e. weight when :math:`j(i) = j(k)`), and second element contains array of cross-term C-weights (i.e. weight when :math:`j(i) \neq j(k)`)
    
    """  
    
    # Number of observations in X, Y, and intersection
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float) # returns no. of observations across all teachers in X (e.g. event X)
    J = sum(Xcounts*Xcounts - Xcounts > 0) 
    
    # Check if weights are teacher-level and that each valid teacher has a weight.
    # Fail if not.
    if not(w is None):
        if (w.ndim != 1):
            raise ValueError("Weight object has wrong dimension. You need to supply teacher-level weights only (i.e. 1 weight per teacher). Check 'w' and try again.")
        elif (len(w) != J):
            raise ValueError("Not enough weights supplied (i.e. some teachers didn't receive weights). Check 'w' and try again.")
        
    # Compute C coefficients
    if (w is None):
        # Unweighted (each teacher receives equal weight
    
        C_jj = (J-1)/J**2/(Xcounts*Xcounts - Xcounts)
        C_jj[(Xcounts*Xcounts - Xcounts) == 0] = 0
        C_jk = -1/J**2*(1/Xcounts).reshape(-1,1).dot((1/Xcounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Xcounts == 0] = 0
    
    else:
        # Weighted (each teacher receives weight corresponding to entries in w)
        w_norm = w / np.sum(w) # Normalised weights
        
        C_jj = w_norm * (1 - w_norm) * (1/(Xcounts*Xcounts - Xcounts))
        C_jj[(Xcounts*Xcounts - Xcounts) == 0] = 0
        C_jk = -(w_norm * w_norm)*(1/Xcounts).reshape(-1,1).dot((1/Xcounts).reshape(1,-1))    # J-by-J, with C_jk as each element.
        
        # Set those with no observations to 0
        C_jk[Xcounts == 0,:] = 0 
        C_jk[:,Xcounts == 0] = 0
    

    return C_jj, C_jk