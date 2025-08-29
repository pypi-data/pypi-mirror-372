import pandas as pd
from metrics_miscellany import datamat as dm
import numpy as np

sqrt3 = np.sqrt(3)  # Avoid repeated evaluation of this for speed...
sqrt2pi = np.sqrt(2*np.pi)

def rectangular(u):
    return (np.abs(u) < sqrt3)/(2*sqrt3)  # Rectangular kernel

def gaussian(u):
    return np.exp(-(u**2)/2)/sqrt2pi # Gaussian kernel

def gram(X,kernel=gaussian,bw=1):
    """
    Construct Gram matrix from vector of data X.
    """
    try:
        idx = X.index
        df = True
        x = X.values
    except AttributeError:
        df = False
        x = X

    assert len(x.shape)==1
    K = kernel((x.reshape((-1,1)) - x.reshape((1,-1)))/bw)

    if df:
        if isinstance(X,(dm.DataVec,dm.DataMat)):
            K = dm.DataMat(K,index=X.index,columns=X.index)
        elif isinstance(X,(pd.Series,pd.DataFrame)):
            K = pd.DataFrame(K,index=X.index,columns=X.index)

    return K



def kernel_regression(X,y,bw,kernel=gaussian):
    """
    Use data (X,y) to estimate E(y|x), using bandwidth bw.
    """
    def mhat(x):
        S = kernel((X-x)/bw) # "Smooths"

        return S.dot(y)/S.sum()

    return mhat

def kernel_regression_variance(X,y,bw,kernel=gaussian):
    """
    Use data (X,y) to estimate E((y-m(x))^2|x), using bandwidth bw.
    """
    # Construct leave-one-out residuals
    K = gram(X,bw=bw,kernel=kernel)
    Km = K - K.dg().dg()

    e2 = (y - (K@y)/K.sum(axis=1))**2
    Ksum = K.sum().sum()

    def sigmahat(x):

        S = kernel((X-x)/bw) # "Smooths"

        return (S**2).dot(e2)/Ksum

    return sigmahat
