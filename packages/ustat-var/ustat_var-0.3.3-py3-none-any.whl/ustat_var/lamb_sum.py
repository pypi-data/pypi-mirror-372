# Dependencies
import numpy as np

# Helper for bias-corrected sum squares for general case
def lamb_sum(X,C_jjX,C_jkX,Y,C_jjY,C_jkY):
    r'''
    Computes bias-corrected product :math:`\lambda = (\sum_{k \neq i} C_{ik}^X a^X) (\sum_{k \neq i} C_{ik}^Y a^Y)`. 
    This function is used in ``ustat_samp_covar``. 
    The :math:`C_{ik}^X` represent the C-weights, which are computed by the ``ustat_var.makec()`` function.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array of teacher mean residuals for a^X
    Y: array
        J-by-:math:`\operatorname{max}(T_j)` array of teacher mean residuals for a^Y
    C_jjX: array
        X's C-weights for identical teachers (generated using ustat_var.makec() function).
    C_jkX: array
        X's C-weights for non-identical teachers (generated using ustat_var.makec() function).
    C_jjY: array
        Y's C-weights for identical teachers (generated using ustat_var.makec() function).
    C_jkY: array 
        Y's C-weights for non-identical teachers (generated using ustat_var.makec() function).

    Returns
    -------
    array
        Array with each row's/teacher's bias-corrected product.
    '''
    Xmeans = np.nanmean(X, axis=1)
    Ymeans = np.nanmean(Y, axis=1)    
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float)
    Ycounts = np.array(np.sum(~np.isnan(Y), axis=1),dtype=float)
    Xmeans[Xcounts < 2] = 0 
    Ymeans[Ycounts < 2] = 0

    XYcounts = np.array(np.sum(~np.isnan(X) & ~np.isnan(Y), axis=1),dtype=float)
    XYcovar = np.nansum((X-Xmeans[:,np.newaxis])*(Y-Ymeans[:,np.newaxis]),1,dtype=float)/(XYcounts-1) # Standard sampling covariance formula between X and Y.
    XYcovar[XYcounts <= 1] = 0  # No sampling covariance if no overlap

    tmpX = C_jkX*Xmeans[np.newaxis,:]*Xcounts[np.newaxis,:]    
    tmpY = C_jkY*Ymeans[np.newaxis,:]*Ycounts[np.newaxis,:]    
    tmpBXY = C_jkX*C_jkY*XYcovar[np.newaxis,:]*XYcounts[np.newaxis,:]    
    tmpc = (XYcounts - 1)**2/XYcounts
    tmpc[XYcounts == 0] = 0
    return (
                (C_jjX*Xmeans*(Xcounts - 1) + 
                    np.sum(tmpX,1) - np.diag(tmpX))*
                (C_jjY*Ymeans*(Ycounts - 1) + 
                    np.sum(tmpY,1) - np.diag(tmpY))

                - (C_jjX*C_jjY*XYcovar*tmpc + ( # Bias correction
                            np.sum(tmpBXY,1) - np.diag(tmpBXY)))
            )



# Helper for bias-corrected sum squares
def lamb_sum_spec(X,C_jjX,C_jkX):
    r'''
    Computes special case bias-corrected product :math:`\lambda = (\sum_{k \neq i} C_{ik}^X a^X)^2`. 
    This function is used in the family of sampling covariance functions in the `ustat_samp_covar` submodule. 
    The :math:`C_{ik}^X` represent the C-weights, which are computed by the ``ustat_var.makec()`` function.

    Parameters
    ----------
    X: array
        J-by-:math:`\operatorname{max}(T_j)` array of teacher mean residuals for a^X
    C_jjX: array
        X's C-weights for identical teachers (generated using ustat_var.makec() function).
    C_jkX: array
        X's C-weights for non-identical teachers (generated using ustat_var.makec() function).

    Returns
    -------
    array
        Array with each row's/teacher's bias-corrected product.
    '''
    Xmeans = np.nanmean(X, axis=1)
    Xcounts = np.array(np.sum(~np.isnan(X), axis=1),dtype=float)
    Xmeans[Xcounts < 2] = 0 
    Xvar = np.nansum((X-Xmeans[:,np.newaxis])*(X-Xmeans[:,np.newaxis]),1,dtype=float)/(Xcounts-1) # Standard sampling covariance formula between X and Y.
    Xvar[Xcounts <= 1] = 0  # No sampling covariance if no overlap

    tmpX = C_jkX*Xmeans[np.newaxis,:]*Xcounts[np.newaxis,:]    
    tmpBX = C_jkX*C_jkX*Xvar[np.newaxis,:]*Xcounts[np.newaxis,:]    
    tmpc = (Xcounts - 1)**2/Xcounts
    tmpc[Xcounts == 0] = 0
    
    return (
                (C_jjX*Xmeans*(Xcounts - 1) + 
                    np.sum(tmpX,1) - np.diag(tmpX))**2

                - (C_jjX*C_jjX*Xvar*tmpc + ( # Bias correction
                            np.sum(tmpBX,1) - np.diag(tmpBX)))
            )

