import statsmodels.api as sm
from statsmodels.stats import correlation_tools
import numpy as np
from numpy.linalg import lstsq
import warnings
import pandas as pd
from . import gmm
from . GMM_class import GMM
from . import utils
from .datamat import DataMat, DataVec
from . import datamat as dm

def ols(X,y,cov_type='HC3',PSD_COV=False):
    """OLS estimator of b in y = Xb + u.

    Returns both estimate b as well as an estimate of Var(b).

    The estimator used for the covariance matrix depends on the
    optional argument =cov_type=.

    If optional flag PSD_COV is set, then an effort is made to ensure that
    the estimated covariance matrix is positive semi-definite.  If PSD_COV is
    set to a positive float, then this will be taken to be the smallest eigenvalue
    of the 'corrected' matrix.
    """
    n,k = X.shape

    est = sm.OLS(y,X).fit()
    b = pd.DataFrame({'Coefficients':est.params.values},index=X.columns)
    if cov_type=='HC3':
        V = est.cov_HC3
    elif cov_type=='OLS':
        XX = X.T@X
        if np.linalg.eigh(XX)[0].min()<0:
            XX = correlation_tools.cov_nearest(XX,method='nearest')
            warnings.warn("X'X not positive (semi-) definite.  Correcting!  Estimated variances should not be affected.")
        V = est.resid.var()*np.linalg.inv(XX)
    elif cov_type=='HC2':
        V = est.cov_HC2
    elif cov_type=='HC1':
        V = est.cov_HC1
    elif cov_type=='HC0':
        V = est.cov_HC0
    else:
        raise ValueError("Unknown type of covariance matrix.")

    if PSD_COV:
        if PSD_COV is True:
            PSD_COV = (b**2).min()
        s,U = np.linalg.eigh((V+V.T)/2)
        if s.min()<PSD_COV:
            oldV = V
            V = U@np.diag(np.maximum(s,PSD_COV))@U.T
            warnings.warn("Estimated covariance matrix not positive (semi-) definite.\nCorrecting! Norm of difference is %g." % np.linalg.norm(oldV-V))

    V = pd.DataFrame(V,index=X.columns,columns=X.columns)

    return b,V

def restricted_tsls(y,X,R=None,r=None,Z=None,cov='HC3'):
    """
    Estimate b in y = Xb + u s.t. Rb = r.

    Return b and lm, a vector of Lagrange multipliers associated with the constraints,
    as well as estimates of Omega = E Z'ee'Z and the covariance matrix of b.
    """
    if Z is None:
        Z = X

    N,k = X.shape
    _,l = Z.shape

    if R is not None:
        m,__ = R.shape
        assert __==k, "Matrix of restrictions must be conformable with vector of parameters."
    else:
        m = 0

    assert N==_, "X & Z must have same number of rows."
    assert l+m>=k, f"Need number of instruments ({l}) plus restrictions ({m}) greater than or equal to number of parameters ({k})."

    Qzz = Z.T@Z/N
    Qxz = X.T@Z/N

    if Qzz.shape==(1,): # Scalar
        Qzzinv = 1/Qzz
    else:
        Qzzinv = Qzz.inv

    Q = N*Qxz@(Qzzinv)@Qxz.T

    if R is not None:
        QRT = dm.concat({'beta':Q,'lm':R.T},axis=1,levelnames=True,toplevelname='parms')
        R0 = dm.concat({'beta':R,
                        'lm':dm.DataMat(index=R.index,columns=R.index).fillna(0)},
                       axis=1,levelnames=True,toplevelname='parms')
        lhs = dm.concat({'beta':QRT,'lm':R0},levelnames=True,toplevelname='parms')
        rhs = dm.concat({'beta':Qxz@(Qzzinv)@Z.T@y,'lm':r},levelnames=True,toplevelname='parms')
        XR = dm.concat([X,R.T],axis=1,levelnames=True)
        ZR = dm.concat([Z,R.T],axis=1,levelnames=True)
    else:
        lhs = Q
        rhs = Qxz@(Qzzinv)@Z.T@y
        XR = X
        ZR = Z

    #assert lhs.rank()>=lhs.shape[1], "Rank condition violated"

    B = lhs.lstsq(rhs)

    e = y - XR@B

    if cov=='HC2': # Use prediction errors
        e = e/np.sqrt((1-X.leverage))
    elif cov=='HC3':
        e = e/(1-X.leverage)

    Ze = ZR.multiply(e,axis=0)
    Omega = Ze.T@Ze/N

    # Redfine Qs to include restrictions
    Qzz = ZR.T@ZR/N
    Qxz = XR.T@ZR/N

    if Qzz.shape==(1,): # Scalar
        Qzzinv = 1/Qzz
    else:
        Qzzinv = Qzz.inv

    D = Qxz@Qzzinv@Qxz.T

    if D.shape==(1,): # Scalar
        Dinv = 1/D
    else:
        Dinv = D.inv

    V = Dinv@(Qxz@Qzzinv@Omega@Qzzinv@Qxz.T)@Dinv/N

    if cov=='HC1':
        V = V*(N/(N-k))

    if R is None:
        return B,Omega,V
    else:
        return B,lm,Omega,V

def tsls(X,y,Z,return_Omega=False,**kwargs):
    """
    Two-stage least squares estimator.
    """
    b,Omega,Vb = restricted_tsls(y,X,Z=Z,**kwargs)

    if return_Omega:
        return b,Omega
    else:
        return b,Vb

def factor_analysis(X,n_components=None,noise_variance_init=None,
                    max_its=1000,tol=1e-2,
                    svd_method='eig'):
    """Fit the FactorAnalysis model to X using SVD based MLE approach.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features) Training data.

    n_components : Proposed rank (number of factors)
    """

    n_samples, n_features = X.shape

    assert n_samples >= n_features

    if n_components is None:
        n_components = n_features

    xbar = X.mean(axis=0)
    X = X - xbar

    # some constant terms
    nsqrt = np.sqrt(n_samples)
    llconst = n_features * np.log(2.0 * np.pi) + n_components
    var = X.var()

    if noise_variance_init is None:
        psi = np.ones(n_features)
    else:
        if len(noise_variance_init) != n_features:
            raise ValueError(
                    "noise_variance_init dimension does not accord "
                    "with number of features : %d != %d"
                    % (len(noise_variance_init), n_features)
            )
        psi = np.array(noise_variance_init)

    loglike = []
    old_ll = -np.inf
    SMALL = 1e-12

    def squared_norm(x):
        return np.linalg.norm(x)**2

    def self_inner(X,min_obs=None):
        """Compute inner product X.T@X, allowing for possibility of missing data."""
        n,m=X.shape

        if n<m:
            axis=1
            N=m
        else:
            axis=0
            N=n

        mX = np.ma.masked_invalid(X)

        xbar = np.mean(mX,axis=axis)

        if axis:
            C=(N-1)*np.ma.cov(mX)
        else:
            C=(N-1)*np.ma.cov(mX.T)

        return (C + N*np.outer(xbar,xbar)).data

    # we'll modify svd outputs to return unexplained variance
    # to allow for unified computation of loglikelihood
    if svd_method == "lapack":

        def my_svd(X):
            _, s, Vt = linalg.svd(X, full_matrices=False, check_finite=False)
            return (
                s[:n_components],
                Vt[:n_components],
                squared_norm(s[n_components:]),
            )

    elif svd_method == "randomized":
        random_state = check_random_state(self.random_state)

        def my_svd(X):
            _, s, Vt = randomized_svd(
                X,
                n_components,
                random_state=random_state,
                n_iter=self.iterated_power,
            )
            return s, Vt, squared_norm(X) - squared_norm(s)

    elif svd_method == 'eig':

        def my_svd(P):

            sigmas,v=np.linalg.eigh(P)
            vt = v.T

            order=np.argsort(-sigmas)
            sigmas=sigmas[order]

            # Truncate rank of representation using Kaiser criterion (positive eigenvalues)
            vt=vt[order,:]
            vt=vt[sigmas>0,:]
            s=np.sqrt(sigmas[sigmas>0])

            if n_components is not None and len(s) > n_components:
                vt=vt[:n_components,:]
                s=s[:n_components]

            r=len(s)

            return s, vt, squared_norm(P) - squared_norm(s)

    P = self_inner(X)
    for i in range(max_its):
        # SMALL helps numerics
        sqrt_psi = np.sqrt(psi) + SMALL
        s, Vt, unexp_var = my_svd(P@np.diag(1/(psi * n_samples)))
        s **= 2
        # Use 'maximum' here to avoid sqrt problems.
        W = np.sqrt(np.maximum(s - 1.0, 0.0))[:, np.newaxis] * Vt
        del Vt
        W = W.squeeze()*sqrt_psi

        # loglikelihood
        ll = llconst + np.sum(np.log(s))
        ll += unexp_var + np.sum(np.log(psi))
        ll *= -n_samples / 2.0
        loglike.append(ll)
        if (ll - old_ll) < tol:
            break
        old_ll = ll

        psi = np.maximum(var - np.sum(W**2, axis=0), SMALL)
    else:
        if max_its==0: # Use hill-climbing
            def ll():
                ll = llconst + np.sum(np.log(s))
                ll += unexp_var + np.sum(np.log(psi))
                ll *= -n_samples / 2.0

        else:
            warnings.warn(
                "FactorAnalysis did not converge."
                + " You might want"
                + " to increase the number of iterations.",
                ConvergenceWarning,
            )

    return W, psi

def fwl_regression_step(D,X):
    """Regress each datamat in dictionary D on X.
       Return a dictionary of residuals, and a dictionary of least-squares coefficients.
    """
    b = {}
    u = {}
    if len(D)==0: return D,{}

    for k,v in D.items():
        b[k] = X.lstsq(v)
        u[k] = dm.DataMat(v.resid(X))

    return u,b

def fwl_regression(D,B=None,U=None):
    """Regress each datamat in dictionary D on the last element X of D.
       Iterate.

       Return a dictionary of residuals, and a dictionary of least-squares coefficients.
    """
    if B is None: B={}
    if U is None: U={}

    if len(D)==0:
        return {},{}
    elif len(D)==1:
        return U,B
    else:
        xk,x = D.popitem()
        D,B[xk] = fwl_regression_step(D,x)
        U[xk] = D.copy()
        return fwl_regression(D,B=B,U=U)

def reconstruct_coefficients_from_fwl(B: dict,as_dict=False):
    """
    Reconstructs OLS coefficient vectors from FWL inputs,
    generalized for matrix regressors.
    """
    # ## 1. Infer the dependent variable name ##
    top_level_keys = set(B.keys())
    if len(top_level_keys)==0: return {}

    # Arbitrarily pick the first variable's sub-dictionary to inspect its keys
    first_var_key = next(iter(B))
    all_nested_keys = set(B[first_var_key].keys())

    # The dependent variable is the key in the nested dict that is NOT a top-level key
    dep_var_set = all_nested_keys - top_level_keys
    if len(dep_var_set) != 1:
        raise ValueError("Could not uniquely determine the dependent variable name.")
    dep_var_name = dep_var_set.pop()

    # ## 2. Proceed with the iterative reconstruction ##
    ordered_vars = list(B.keys())
    p = len(ordered_vars)
    coeffs = {}  # Stores the final coefficient vectors (b_i)

    # This loop proceeds backward from i = p-1 down to 0
    for i in range(p - 1, -1, -1):
        current_var = ordered_vars[i]

        # Use the inferred dependent variable name to get the G_iy vector
        G_iy = B[current_var][dep_var_name]

        summation_vector = np.zeros_like(G_iy)

        for j in range(i + 1, p):
            successor_var = ordered_vars[j]
            G_ij = B[current_var][successor_var]
            b_j = coeffs[successor_var]
            summation_vector += G_ij @ b_j

        coeffs[current_var] = G_iy - summation_vector
        coeffs[current_var].name = dep_var_name

    # Reverse order of dict
    coeffs = {k:coeffs[k] for k in reversed(list(coeffs.keys()))}

    if as_dict:
        return coeffs
    else:
        return dm.concat(coeffs,levelnames=True).squeeze()

def linear_gmm(X,y,Z,W=None,return_Omega=False):
    """
    Linear GMM estimator.
    """

    if W is None: # Use 2sls to get initial estimate of W
        b1,Omega1 = tsls(X,y,Z,return_Omega=True)
        W = Omega1.inv
        return linear_gmm(X,y,Z,W=W)
    else:
        n,k = X.shape

        Qxz = X.T@Z/n

        b = lstsq(Qxz@W@Qxz.T,Qxz@W@Z.T@y/n,rcond=None)[0]

        b = pd.Series(b.squeeze(),index=X.columns)

        # Cov matrix
        e = y.squeeze() - X@b

        #Omega = Z.T@(e**2).dg()@Z/n
        # Rather than forming even a sparse nxn matrix, just use element-by-element multiplication
        ZTe = Z.T.multiply(e)
        Omega = ZTe@ZTe.T/n

        if return_Omega:
            return b,Omega
        else:
            Vb = (Qxz@Omega.inv@Qxz.T).inv/n
            return b,Vb

def restricted_linear_gmm(X,y,Z,R,r,W=None,return_Omega=False):
    """
    Linear GMM estimator.
    """
    raise NotImplementedError
    if W is None: # Use 2sls to get initial estimate of W
        b1,Omega1 = tsls(X,y,Z,return_Omega=True)
        W = Omega1.inv
        return linear_gmm(X,y,Z,W=W)
    else:
        n,k = X.shape

        Qxz = X.T@Z/n

        b = lstsq(Qxz@W@Qxz.T,Qxz@W@Z.T@y/n,rcond=None)[0]

        b = pd.Series(b.squeeze(),index=X.columns)

        # Cov matrix
        e = y.squeeze() - X@b

        #Omega = Z.T@(e**2).dg()@Z/n
        # Rather than forming even a sparse nxn matrix, just use element-by-element multiplication
        ZTe = Z.T.multiply(e)
        Omega = ZTe@ZTe.T/n

        if return_Omega:
            return b,Omega
        else:
            Vb = (Qxz@Omega.inv@Qxz.T).inv/n
            return b,Vb

def factor_regression(Y,X,F=None,rank=1,tol=1e-3):

    if rank>1:
        raise NotImplementedError("Factor regression for rank>1 is not reliable.")

    N,k = Y.shape
    def ols(X,Y):
        N,k = Y.shape
        XX = utils.self_inner(X)/N
        XY = utils.matrix_product(X.T,Y)/N
        B = np.linalg.lstsq(XX,XY,rcond=None)[0]
        return pd.DataFrame(B,index=X.columns,columns=Y.columns)

    if F is None:
        B = ols(X,Y)
        F = 0
    else:
        parms = ols(pd.concat([X,F],axis=1),Y)
        L = parms.iloc[-rank:,:]
        B = parms.iloc[:-rank,:]

    lastF = F
    F,s,vt = utils.svd_missing(Y - utils.matrix_product(X,B),max_rank=rank)
    scale = F.std()
    F = F.multiply(1/scale)

    if np.linalg.norm(F-lastF)>tol:
        B,L,F = factor_regression(Y,X,F=F,rank=rank,tol=tol)

    return B,L,F
