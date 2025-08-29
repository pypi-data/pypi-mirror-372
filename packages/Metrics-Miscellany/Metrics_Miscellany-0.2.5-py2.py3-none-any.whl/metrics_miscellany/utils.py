import numpy as np
from scipy import sparse as scipy_sparse
import pandas as pd

def inv(A):
    """Inverse of square pandas DataFrame."""
    if np.isscalar(A): A = pd.DataFrame(np.array([[A]]))

    B = np.linalg.inv(A)
    return pd.DataFrame(B,columns=A.columns,index=A.index)

def pinv(A):
    """Moore-Penrose pseudo-inverse of A.

    >>> A = pd.DataFrame([[1,2,3],[4,5,6]])
    >>> np.allclose(A@pinv(A),np.eye(2))
    True
    """
    if np.isscalar(A): A = pd.DataFrame(np.array([[A]]))

    B = np.linalg.pinv(A)
    return pd.DataFrame(B,columns=A.index,index=A.columns)

def leverage(X):
    """
    Leverage of matrix X; i.e., diagonal of projection matrix.
    """
    return (X*pinv(X).T).sum(axis=1)

def svd(A,hermitian=False):
    """Singular value composition into U@S.dg@V.T."""
    idx = A.index
    cols = A.columns
    u,s,vt = np.linalg.svd(A,compute_uv=True,full_matrices=False,hermitian=hermitian)
    u = pd.DataFrame(u,index=idx)
    vt = pd.DataFrame(vt,columns=cols)
    s = pd.Series(s)

    return u,s,vt

def eig(A,hermitian=False):
    """Singular value composition into U@S.dg@V.T."""
    idx = A.index
    cols = A.columns
    if hermitian:
        s2,u = np.linalg.eigh(A)
    else:
        s2,u = np.linalg.eig(A)

    s2 = np.flip(s2)
    u = np.fliplr(u)

    u = pd.DataFrame(u,index=idx,columns=cols)
    s2 = pd.Series(s2.squeeze())

    return s2,u

def diag(X,sparse=True):

    try:
        assert X.shape[0] == X.shape[1]
        d = pd.Series(np.diag(X),index=X.index)
    except IndexError: # X is a series?
        if sparse:
            # We can wind up blowing ram if not careful...
            d = scipy_sparse.diags(X.values)
            d = pd.DataFrame.sparse.from_spmatrix(d,index=X.index,columns=X.index)
        else:
            raise NotImplementedError
    except AttributeError: # Not a pandas object?
        d = np.diag(X)

    return d

def outer(S,T):
    """Outer product of two series (vectors) S & T.
    """
    return pd.DataFrame(np.outer(S,T),index=S.index,columns=T.index)

def matrix_product(X,Y,strict=False,fillmiss=True):
    """Compute matrix product X@Y, allowing for possibility of missing data.

    The "strict" flag if set requires that the names of levels of indices that vary for columns of X be in the intersection of names of levels of indices that vary for rows of Y.
    """

    if strict and not all(X.columns==Y.index):  # Columns and Indices don't match.
        X.columns = drop_vestigial_levels(X.columns)
        Y.index = drop_vestigial_levels(Y.index)

    if fillmiss:
        X = X.fillna(0)
        Y = Y.fillna(0)

    prod = np.dot(X,Y) #.squeeze()

    if len(prod.shape)==1 or prod.shape[1]==1:
        out = pd.Series(prod.squeeze(),index=X.index)
    else:
        try:
            cols = Y.columns
        except AttributeError:
            cols = None
        out = pd.DataFrame(prod,index=X.index,columns=cols)

    return out

def self_inner(X,min_obs=None):
    """Compute inner product X.T@X, allowing for possibility of missing data."""
    n,m=X.shape

    if n<m:
        axis=1
        N=m
    else:
        axis=0
        N=n

    xbar=X.mean(axis=axis)

    if axis:
        C=(N-1)*X.T.cov(min_periods=min_obs)
    else:
        C=(N-1)*X.cov(min_periods=min_obs)

    return C + N*np.outer(xbar,xbar)

def kron(A,B,sparse=False):
    if sparse:
        from scipy.sparse import kron

    if isinstance(A,pd.DataFrame):
        a = A.values
        if isinstance(B,pd.DataFrame):
            columns = pd.MultiIndex.from_tuples([(*i,*j) for i in A.columns for j in B.columns],                                               names=A.columns.names+B.columns.names)
            b = B.values
        else:
            columns = A.columns.remove_unused_levels()
            b = B.values.reshape((-1,1))
    elif isinstance(B,pd.DataFrame):
        columns = B.columns.remove_unused_levels()
        a = A.values.reshape((-1,1))
        b = B.values

    index = pd.MultiIndex.from_tuples([(*i,*j) for i in A.index for j in B.index],
                                      names=A.index.names+B.index.names)

    if sparse:
        a = kron(a,b)
        return pd.DataFrame.sparse.from_spmatrix(a,columns=columns,index=index)
    else:
        a = np.kron(a,b)
        return pd.DataFrame(a,columns=columns,index=index)

def heteropca(C,r=1,max_its=50,tol=1e-3,verbose=False):
    """Estimate r factors and factor weights of covariance matrix C."""
    from scipy.spatial import procrustes

    N = C - np.diag(np.diag(C))

    ulast = np.zeros((N.shape[1],r))
    u = np.zeros((N.shape[1],r))
    u[0,0] = 1
    ulast[-1,0] = 1

    t = 0

    while procrustes(u,ulast)[-1] >tol and t<max_its:
        ulast = u

        u,s,vt = np.linalg.svd(N,full_matrices=False,hermitian=True)

        s = s[:r]
        u = u[:,:r]

        Ntilde = u[:,:r]@np.diag(s[:r])@vt[:r,:]

        N = N - np.diag(np.diag(N)) + np.diag(np.diag(Ntilde))

        t += 1

        if t==max_its:
            warnings.warn("Exceeded maximum iterations (%d)" % max_its)
        if verbose: print(f"Iteration {t}, u[0,:r]={u[0,:r]}.")

    return u,s

def svd_missing(A,max_rank=None,min_obs=None,heteroskedastic=False,verbose=False):
    """Singular Value Decomposition with missing values

    Returns matrices U,S,V.T, where A~=U*S*V.T.

    Inputs:
        - A :: matrix or pd.DataFrame, with NaNs for missing data.

        - max_rank :: Truncates the rank of the representation.  Note
                      that this impacts which rows of V will be
                      computed; each row must have at least max_rank
                      non-missing values.  If not supplied rank may be
                      truncated using the Kaiser criterion.

        - min_obs :: Smallest number of non-missing observations for a
                     row of U to be computed.

        - heteroskedastic :: If true, use the "heteroPCA" algorithm
                       developed by Zhang-Cai-Wu (2018) which offers a
                       correction to the svd in the case of
                       heteroskedastic errors.  If supplied as a pair,
                       heteroskedastic[0] gives a maximum number of
                       iterations, while heteroskedastic[1] gives a
                       tolerance for convergence of the algorithm.

    Ethan Ligon                                        September 2021

    """
    # Defaults; modify by passing a tuple to heteroskedastic argument.
    max_its=50
    tol = 1e-3

    P = self_inner(A,min_obs=min_obs) # P = A.T@A

    sigmas,v=np.linalg.eigh(P)

    order=np.argsort(-sigmas)
    sigmas=sigmas[order]

    # Truncate rank of representation using Kaiser criterion (positive eigenvalues)
    v=v[:,order]
    v=v[:,sigmas>0]
    s=np.sqrt(sigmas[sigmas>0])

    if max_rank is not None and len(s) > max_rank:
        v=v[:,:max_rank]
        s=s[:max_rank]

    r=len(s)

    if heteroskedastic: # Interpret tuple
        try:
            max_its,tol = heteroskedastic
        except TypeError:
            pass
        Pbar = P.mean()
        v,s = heteropca(P-Pbar,r=r,max_its=max_its,tol=tol,verbose=verbose)

    if A.shape[0]==A.shape[1]: # Symmetric; v=u
        return v,s,v.T
    else:
        vs=v@np.diag(s)

        u=np.zeros((A.shape[0],len(s)))
        for j in range(A.shape[0]):
            a=A.iloc[j,:].values.reshape((-1,1))
            x=np.nonzero(~np.isnan(a))[0] # non-missing elements of vector a
            if len(x)>=r:
                u[j,:]=(np.linalg.pinv(vs[x,:])@a[x]).reshape(-1)
            else:
                u[j,:]=np.nan

    s = pd.Series(s)
    u = pd.DataFrame(u,index=A.index)
    v = pd.DataFrame(v,index=A.columns)

    return u,s,v

def sqrtm(A,hermitian=False):
    """
    Return a positive semi-definite square root for the matrix A.

    NB: A must itself be positive semi-definite.
    """
    u,s,vt = svd(A,hermitian=hermitian)

    if np.any(s<0):
        raise ValueError("Matrix must be positive semi-definite.")

    return u@np.diag(np.sqrt(s))@vt

def cholesky(A):
    """
    Cholesky decomposition A = L@L.T; return lower-triangular L.
    """
    L = np.linalg.cholesky(A)
    return pd.DataFrame(L,index=A.index,columns=A.columns)

from pandas import concat, get_dummies, MultiIndex

def drop_missing(X,infinities=False):
    """
    Return tuple of pd.DataFrames in X with any
    missing observations dropped.  Assumes common index.

    If infinities is false values of plus or minus infinity are
    treated as missing values.
    """

    if isinstance(X,dict):
        return dict(zip(X.keys(),drop_missing(list(X.values()),infinities=False)))

    for i,x in enumerate(X):
        if type(x)==pd.Series and x.name is None:
            x.name = i

    foo=pd.concat(X,axis=1)
    if not infinities:
        foo.replace(np.inf,np.nan)
        foo.replace(-np.inf,np.nan)

    foo = foo.dropna(how='any')

    assert len(set(foo.columns))==len(foo.columns) # Column names must be unique!

    Y=[]
    for x in X:
        Y.append(foo.loc[:,pd.DataFrame(x).columns])

    return tuple(Y)

def dummies(df,cols,suffix=False):
    """From a dataframe df, construct an array of indicator (dummy) variables,
    with a column for every unique row df[cols]. Note that the list cols can
    include names of levels of multiindices.

    The optional argument =suffix=, if provided as a string, will append suffix
    to column names of dummy variables. If suffix=True, then the string '_d'
    will be appended.
    """
    idxcols = list(set(df.index.names).intersection(cols))
    colcols = list(set(cols).difference(idxcols))

    if len(idxcols):
        idx = use_indices(df,idxcols)
        v = concat([idx,df[colcols]],axis=1)
    else:
        v = df[colcols]

    usecols = []
    for s in idxcols+colcols:
        usecols.append(v[s].squeeze())

    tuples = pd.Series(list(zip(*usecols)),index=v.index)

    v = get_dummies(tuples).astype(int)

    if suffix==True:
        suffix = '_d'

    if suffix!=False and len(suffix)>0:
        columns = [tuple([str(c)+suffix for c in t]) for t in v.columns]
    else:
        columns = v.columns

    v.columns = MultiIndex.from_tuples(columns,names=idxcols+colcols)

    return v

import pandas as pd

def use_indices(df,idxnames):
    if len(set(idxnames).intersection(df.index.names))==0:
        return pd.DataFrame(index=df.index)

    try:
        idx = df.index
        df = df.reset_index()[idxnames]
        df.index = idx
        return df
    except InvalidIndexError:
        return df

def drop_vestigial_levels(idx,axis=0,both=False,multiindex=True):
    """
    Drop levels that don't vary across the index.

    >>> idx = pd.MultiIndex.from_tuples([(1,1),(1,2)],names=['i','j'])
    >>> drop_vestigial_levels(idx)
    Index([1, 2], dtype='int64', name='j')
    """
    if both:
        return drop_vestigial_levels(drop_vestigial_levels(idx,axis=1))

    if axis==1:
        idx = idx.T

    if isinstance(idx,(pd.DataFrame,pd.Series)):
        df = idx
        idx = df.index
        HumptyDumpty = True
    else:
        HumptyDumpty = False

    try:
        l = 0
        L = len(idx.levels)
        while l < L:
            if len(set(idx.codes[l]))<=1:
                idx = idx.droplevel(l)
                L -= 1
            else:
                l += 1
                if l>=L: break
    except AttributeError:
        pass

    if multiindex and not isinstance(idx,pd.MultiIndex): # Return a multiindex, not an Index
        idx = pd.MultiIndex.from_tuples(idx.str.split('|').tolist(),names=[idx.name])

    if HumptyDumpty:
        df.index = idx
        idx = df
        if axis==1:
            idx = idx.T

    return idx

import numpy as np
import pandas as pd

def qr(X):
    """
    Pandas-friendly QR decomposition.
    """
    assert X.shape[0]>=X.shape[1]

    Q,R = np.linalg.qr(X)
    Q = pd.DataFrame(Q,index=X.index, columns=X.columns)
    R = pd.DataFrame(R,index=X.columns, columns=X.columns)

    return Q,R

def leverage(X):
    """
    Return leverage of observations in X (the diagonals of the hat matrix).
    """

    Q = qr(X)[0]

    return (Q**2).sum(axis=1)

def hat_factory(X):
    """
    Return a function hat(y) that returns X(X'X)^{-1}X'y.

    This is the least squares prediction of y given X.

    We use the fact that  the hat matrix is equal to QQ',
    where Q comes from the QR decomposition of X.
    """
    Q = qr(X)[0]

    def hat(y):
        return Q@(Q.T@y)

    return hat

from statsmodels.stats.correlation_tools import cov_nearest as _cov_nearest
import pandas as pd

def cov_nearest(V,threshold=1e-12):
    """
    Return a positive definite matrix which is "nearest" to the symmetric matrix V,
    with the smallest eigenvalue not less than threshold.
    """
    s,U = np.linalg.eigh((V+V.T)/2) # Eigenvalue decomposition of symmetric matrix

    s = np.maximum(s,threshold)

    return V*0 + U@np.diag(s)@U.T  # Trick preserves attributes of dataframe V

import pandas as pd
import numpy as np

def trim(df,alpha):
    """Trim values below alpha quantile and above (1-alpha) quantile.

    This maps individual extreme elements of df to NaN.
    """
    xmin = df.quantile(alpha)
    xmax = df.quantile(1-alpha)
    return df.where((df>=xmin)*(df<=xmax),np.nan)
