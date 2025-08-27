'''Contains all functions to estimate sampling variances and covariances'''

# Dependencies:
import numpy as np
from .sampc import sampc
from .makec import makec, makec_spec
from .lamb_sum import lamb_sum, lamb_sum_spec


# Estimate most general case A != B != C != D
def ustat_samp_covar(Atmp,Btmp,Ctmp,Dtmp, w=None):
    r'''
    Estimates the sampling covariance between the estimate of 
    :math:`\operatorname{Cov}(a^A, a^B)` and the estimates of :math:`\operatorname{Cov}(a^C, a^D)`.

    By setting :math:`A=B=C=D`, for example, one will simply get the sampling variance of a variance estimate.
    
    Parameters
    ----------
    Atmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome A
    Btmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome D
    Ctmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome C
    Dtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome D
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A, B, C, and D, and must be 1-dimensional (e.g. one weight per teacher/row).

    Returns
    -------
    float
        a float representing the sampling covariance :math:`Cov(Cov(a^A,a^B), Cov(a^C,a^D))`
    '''
    # Make copies
    A = Atmp.copy()
    B = Btmp.copy()
    C = Ctmp.copy()
    D = Dtmp.copy()

    # Compute sampling covariances
    sigAC = sampc(A,C) # These are standard formulae; i.e., sampc(X, Y) = (X - Xmean) * (Y - Ymean) / (|XY| - 1)
    sigAD = sampc(A,D)
    sigBC = sampc(B,C)
    sigBD = sampc(B,D)

    # Counts
    # Count the cardinality of the intersections between matrices A and C, and so on.
    countsAC = np.array(np.sum(~np.isnan(A) & ~np.isnan(C), axis=1),dtype=float) 
    countsAD = np.array(np.sum(~np.isnan(A) & ~np.isnan(D), axis=1),dtype=float)
    countsBC = np.array(np.sum(~np.isnan(B) & ~np.isnan(C), axis=1),dtype=float)
    countsBD = np.array(np.sum(~np.isnan(B) & ~np.isnan(D), axis=1),dtype=float)
    countsABCD = np.array(np.sum(~np.isnan(A) & ~np.isnan(C)
                    & ~np.isnan(B) & ~np.isnan(D), axis=1),dtype=float)

    # Compute Ciks.
    if (w is None):
        # Compute unweighted C coefficients
        
        C_jjAB, C_jkAB = makec(A,B)
        C_jjCD, C_jkCD = makec(C,D)
        C_jjBA, C_jkBA = makec(B,A) # Add reverse
        C_jjDC, C_jkDC = makec(D,C)
    
    else:
        # Compute j-weighted C coefficient
        C_jjAB, C_jkAB = makec(A,B, w = w)
        C_jjCD, C_jkCD = makec(C,D, w = w)
        C_jjBA, C_jkBA = makec(B,A, w = w) # Add reverse
        C_jjDC, C_jkDC = makec(D,C, w = w)


    # Compute bias corrected products of sums
    prodABBCDD = lamb_sum(B, C_jjAB, C_jkAB, D, C_jjCD, C_jkCD)
    prodABBDCC = lamb_sum(B, C_jjAB, C_jkAB, C, C_jjDC, C_jkDC)
    prodBAACDD = lamb_sum(A, C_jjBA, C_jkBA, D, C_jjCD, C_jkCD)
    prodBAADCC = lamb_sum(A, C_jjBA, C_jkBA, C, C_jjDC, C_jkDC)
    
    # Variance calulation
    vsum = (
            countsAC*sigAC*prodABBCDD +
            countsAD*sigAD*prodABBDCC +
            countsBC*sigBC*prodBAACDD +
            countsBD*sigBD*prodBAADCC 
            )

    # Add last piece
    tmpC = C_jkAB * C_jkDC * sigBC[np.newaxis,:] * countsBC[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigAD*countsAD*tmpC
    vsum += sigAD*C_jjAB*C_jjDC*sigBC*(countsAD*countsBC - countsABCD) 

    tmpC = C_jkAB * C_jkCD * sigBD[np.newaxis,:] * countsBD[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigAC*countsAC*tmpC
    vsum += sigAC*C_jjAB*C_jjCD*sigBD*(countsBD*countsAC - countsABCD) 

    return np.sum(vsum)

# Special case when A = B = C = D
def vcv_samp_covar_XXXX(Xtmp, w=None):
    r'''
    Estimates the sampling :math:`Var(Var(a^X))`. 
    Equivalent to calling `ustat_samp_covar(X,X,X,X)`, except faster due to fewer required underlying function calls.

    Parameters
    ----------
    Xtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome A
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A and must be 1-dimensional (e.g. one weight per teacher/row).

    Returns
    -------
    float
        a float representing the sampling variance :math:`Var(Var(a^X))`
    '''

    # Make copies
    A = Xtmp.copy()

    # Compute sampling covariances
    sigAA = sampc(A,A) # These are standard formulae; i.e., sampc(X, Y) = (X - Xmean) * (Y - Ymean) / (|XY| - 1)

    # Counts
    # Count the cardinality of the intersections between matrices A and C, and so on.
    countsA = np.array(np.sum(~np.isnan(A), axis=1),dtype=float) 

    # Compute Ciks
    if w is None:
        C_jjAA, C_jkAA = makec_spec(A)
    else:
        C_jjAA, C_jkAA = makec_spec(A,w=w)

    # Compute bias corrected products of sums
    prodA = lamb_sum_spec(A, C_jjAA, C_jkAA)
    
    # Variance calulation
    vsum = (
            4*countsA*sigAA*prodA
            )

    # Add last piece
    tmpC = C_jkAA**2 * sigAA[np.newaxis,:] * countsA[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += 2*sigAA*countsA*tmpC
    vsum += 2*sigAA*C_jjAA*C_jjAA*sigAA*(countsA*countsA - countsA) 

    return np.sum(vsum)

# Special case when A = C != B = D

def vcv_samp_covar_XYXY(Xtmp, Ytmp, w=None):
    '''
    Estimates sampling :math:`Var(Cov(a^X, a^Y))`. 
    Equivalent to calling `ustat_samp_covar(X,Y,X,Y)`, except faster due to fewer required underlying function calls.

    Parameters
    ----------
    Xtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    Ytmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome Y
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A and C, and must be 1-dimensional (e.g. one weight per teacher/row).
    
    Returns
    -------
    float
        a float representing the sampling variance :math:`Var(Cov(a^X, a^Y))`

    '''
    
    # Make copies
    A = Xtmp.copy()
    C = Ytmp.copy()

    # Compute sampling covariances
    sigAC = sampc(A,C) # These are standard formulae; i.e., sampc(X, Y) = (X - Xmean) * (Y - Ymean) / (|XY| - 1)
    sigA = sampc(A,A)
    sigC = sampc(C,C)
    
    # Counts
    # Count the cardinality of the intersections between matrices A and C, and so on.
    countsAC = np.array(np.sum(~np.isnan(A) & ~np.isnan(C), axis=1),dtype=float)
    countsA = np.array(np.sum(~np.isnan(A), axis=1),dtype=float)
    countsC = np.array(np.sum(~np.isnan(C), axis=1),dtype=float)
    
    # Compute Ciks
    if w is None:
        C_jjAC, C_jkAC = makec(A,C)
        C_jjCA, C_jkCA = makec(C,A)
    else:
        C_jjAC, C_jkAC = makec(A,C, w=w)
        C_jjCA, C_jkCA = makec(C,A, w=w)

    # Compute bias corrected products of sums
    prodACC = lamb_sum_spec(C, C_jjAC, C_jkAC)
    prodCAA = lamb_sum_spec(A, C_jjCA, C_jkCA)
    prodACCCAA = lamb_sum(C, C_jjAC, C_jkAC, A, C_jjCA, C_jkCA)
    
    # Variance calulation
    vsum = (countsA * sigA * prodACC +
            countsC * sigC * prodCAA + 
            2*countsAC*sigAC*prodACCCAA)

    # Add last piece
    tmpC = C_jkAC * C_jkCA * sigAC[np.newaxis,:] * countsAC[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigAC*countsAC*tmpC
    vsum += sigAC*C_jjAC*C_jjCA*sigAC*(countsAC*countsAC - countsAC) 

    tmpC = C_jkAC * C_jkAC * sigC[np.newaxis,:] * countsC[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigA*countsA*tmpC
    vsum += sigA*C_jjAC*C_jjAC*sigC*(countsA*countsC - countsAC) 

    return np.sum(vsum)


# Estimate the sampling covariance between two sampling estimates
def vcv_samp_covar_XXXY(Xtmp, Ytmp, w=None):
    r'''
    Estimates sampling :math:`Cov(Var(a^X), Cov(a^X,a^Y))`.
    Equivalent to calling `ustat_samp_covar(X,X,X,Y)`, except faster due to fewer required underlying function calls.

    Parameters
    ----------
    Xtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    Ytmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome Y
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A, D, and must be 1-dimensional (e.g. one weight per teacher/row).
    
    Returns
    -------
    float
        a float representing the sampling covariance :math:`Cov(Var(a^X), Cov(a^X, a^Y))`.

    '''
    # Make copies
    A = Xtmp.copy()
    D = Ytmp.copy()

    # Compute sampling covariances
    sigAA = sampc(A,A) # These are standard formulae; i.e., sampc(X, Y) = (X - Xmean) * (Y - Ymean) / (|XY| - 1)
    sigAD = sampc(A,D)

    # Counts
    # Count the cardinality of the intersections between matrices A and C, and so on.
    countsAA = np.array(np.sum(~np.isnan(A), axis = 1), dtype = float)
    countsAD = np.array(np.sum(~np.isnan(A) & ~np.isnan(D), axis=1),dtype=float)


    # Compute Ciks.
    if (w is None):
        # Compute unweighted C coefficients
        C_jjAA, C_jkAA = makec_spec(A)
        C_jjAD, C_jkAD = makec(A,D)
        C_jjDA, C_jkDA = makec(D,A)
    
    else:
        # Compute j-weighted C coefficient
        C_jjAA, C_jkAA = makec_spec(A, w = w)
        C_jjAD, C_jkAD = makec(A,D, w = w)
        C_jjDA, C_jkDA = makec(D,A, w = w)


    # Compute bias corrected products of sums
    prodAAAADD = lamb_sum(A, C_jjAA, C_jkAA, D, C_jjAD, C_jkAD)
    prodAAADAA = lamb_sum(A, C_jjAA, C_jkAA, A, C_jjDA, C_jkDA)
    
    # Variance calulation
    vsum = (
            2*countsAA*sigAA*prodAAAADD +
            2*countsAD*sigAD*prodAAADAA
            )

    # Add last piece
    tmpC = C_jkAA * C_jkDA * sigAA[np.newaxis,:] * countsAA[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigAD*countsAD*tmpC
    vsum += sigAD*C_jjAA*C_jjDA*sigAA*(countsAD*countsAA - countsAD) 

    tmpC = C_jkAA * C_jkAD * sigAD[np.newaxis,:] * countsAD[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += sigAA*countsAA*tmpC
    vsum += sigAA*C_jjAA*C_jjAD*sigAD*(countsAD*countsAA - countsAD) 

    return np.sum(vsum)


# Special case when A = B != C = D
def vcv_samp_covar_XXYY(Xtmp,Ytmp, w=None):
    r'''
    Estimates the sampling :math:`Cov(Var(a^X), Var(a^Y))`. 
    Equivalent to calling `ustat_samp_covar(X,X,Y,Y)`, except faster due to fewer required underlying function calls.
    
    Parameters
    ----------
    Xtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome X
    Ytmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome Y
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A, B, C, and D, and must be 1-dimensional (e.g. one weight per teacher/row).
    
    Returns
    -------
    float
        a float representing the sampling covariance :math:`Cov(Var(a^X), Var(a^Y))`.
    
    '''
    # Make copies
    A = Xtmp.copy()
    D = Ytmp.copy()

    # Compute sampling covariances
    sigAD = sampc(A,D) # These are standard formulae; i.e., sampc(X, Y) = (X - Xmean) * (Y - Ymean) / (|XY| - 1)

    # Counts
    # Count the cardinality of the intersections between matrices A and C, and so on.
    countsAD = np.array(np.sum(~np.isnan(A) & ~np.isnan(D), axis=1),dtype=float) 


    # Compute Ciks.
    if (w is None):
        # Compute unweighted C coefficients 
        C_jjAA, C_jkAA = makec_spec(A)
        C_jjDD, C_jkDD = makec_spec(D)
    
    else:
        # Compute j-weighted C coefficient
        C_jjAA, C_jkAA = makec_spec(A, w = w)
        C_jjDD, C_jkDD = makec_spec(D, w = w)


    # Compute bias corrected products of sums
    prodAAADDD = lamb_sum(A, C_jjAA, C_jkAA, D, C_jjDD, C_jkDD)
    
    # Variance calulation
    vsum = (
            4 * countsAD * sigAD * prodAAADDD
            )

    # Add last piece
    tmpC = C_jkAA * C_jkDD * sigAD[np.newaxis,:] * countsAD[np.newaxis,:]
    tmpC = (np.sum(tmpC, 1) - np.diag(tmpC))
    vsum += 2 * (sigAD * countsAD * tmpC)
    vsum += 2 * (sigAD*C_jjAA*C_jjDD*sigAD*(countsAD*countsAD - countsAD)) 

    return np.sum(vsum)


# Wrapper function to nest all cases
def ustat_samp_covar_fast(Atmp, Btmp, Ctmp, Dtmp, w = None):
    '''
    Estimates the sampling covariance between the estimate of 
    :math:`\operatorname{Cov}(a^A, a^B)` and the estimates of :math:`\operatorname{Cov}(a^C, a^D)`.    
    Calling `ustat_samp_covar_fast(A,B,C,D)` is equivalent to, but often faster than, calling `ustat_samp_covar(A,B,C,D)`.
    Fundamentally, this function calls `vcv_samp_covar_XXXX()`, `vcv_samp_covar_XXXY()`, `vcv_samp_covar_XXYY()`, and `vcv_samp_covar_XYXY()`.
    
    By setting :math:`A=B=C=D`, for example, one will simply get the sampling variance of a variance estimate.
    
    Parameters
    ----------
    Atmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome A
    Btmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome D
    Ctmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome C
    Dtmp: array
        J-by-:math:`\operatorname{max}(T_j)` array containing data/residuals for outcome D
    w: array 
        Row-wise/teacher-level weights (optional). 
        If included, must have the same number of elements as rows of A, B, C, and D, and must be 1-dimensional (e.g. one weight per teacher/row).
    
    Returns
    -------
    float
        a float representing the sampling covariance :math:`Cov(Cov(a^A, a^B), Cov(a^C, a^D))`
    '''

    ## Check equality of supplied arrays
    # Note, set equal_nan = True so that NaNs in the same spot contain as equal. 
    # Allows function to support unbalanced panels.
    AB_equal = np.array_equal(Atmp, Btmp, equal_nan = True)
    AC_equal = np.array_equal(Atmp, Ctmp, equal_nan = True)
    CD_equal = np.array_equal(Ctmp, Dtmp, equal_nan = True)
    BD_equal = np.array_equal(Btmp, Dtmp, equal_nan = True)

    ## Determine which special case to use.
    if AB_equal and CD_equal and AC_equal:
        # A = B, C = D, and A = C implies Cov(Cov(A,A), Cov(A,A)) = Var(Var(A))
        type_computed = "v(v(x))"
        samp_var = vcv_samp_covar_XXXX(Xtmp=Atmp, w=w)

    elif AB_equal and CD_equal and not(AC_equal):
        # A = B, C = D, but A != C implies Cov(Cov(A,A), Cov(C,C)) = Cov(Var(A), Var(C))
        type_computed = "cov(v(x), v(y))"
        samp_var = vcv_samp_covar_XXYY(Xtmp=Atmp, Ytmp=Ctmp, w=w)

    elif AB_equal and not(CD_equal) and AC_equal:
        # A = B and A = C, but C != D implies Cov(Cov(A,A), Cov(A,D)) = Cov(Var(A), Cov(A,D))
        type_computed = "cov(var(x), cov(x,y))"
        samp_var = vcv_samp_covar_XXXY(Xtmp=Atmp, Ytmp=Dtmp, w=w)

    elif not(AB_equal) and not(CD_equal) and AC_equal and BD_equal:
        # A = C, but A != B and C != D and B = D implies Cov(Cov(A, D), Cov(A, D)) = Var(Cov(A,D))
        type_computed = "var(cov(x,y))"
        samp_var = vcv_samp_covar_XYXY(Xtmp=Atmp, Ytmp=Btmp, w=w)

    else:
        # A != B, C != D, A != C implies Cov(Cov(A,B), Cov(C,D))
        type_computed = "cov(cov(a,b), cov(c,d))"
        samp_var = ustat_samp_covar(Atmp=Atmp, Btmp=Btmp, Ctmp=Ctmp, Dtmp=Dtmp, w=w)

    return samp_var
