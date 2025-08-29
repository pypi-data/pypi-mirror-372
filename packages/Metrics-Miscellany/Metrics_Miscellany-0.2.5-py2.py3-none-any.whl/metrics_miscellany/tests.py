from metrics_miscellany import utils
from scipy import stats
import pandas as pd
import numpy as np

def chi2_test(b,V,var_selection=None,R=None,TEST=False):
    """Construct chi2 test of R'b = 0.

    If R is None then test is b = 0.

    If one wishes to test a hypothesis regarding only a subset of elements of b,
    this subset can be chosen by specifying var_selection as either a query string
    or as a list.
    """

    if var_selection is not None:
        if type(var_selection) is str:
            myb = b.query(var_selection)
        elif type(var_selection) is list:
            myb = b.loc[var_selection]
        else:
            raise(ValueError,"var_selection should be a query string of list of variable names")
    else:
        myb = b


    # Drop parts of matrix not involved in test
    myV = V.reindex(myb.index,axis=0).reindex(myb.index,axis=1)

    myV = utils.cov_nearest(myV,threshold=1e-10)

    if R is not None:
        myV = R.T@myV@R
        myb = R.T@b
        if np.isscalar(myV):
            myV = np.array([[myV]])
            myb = np.array([[myb]])

    if TEST: # Generate values of my that satisfy Var(myb)=Vb and Emyb=0
        myb = myb*0 + stats.multivariate_normal(cov=((1e0)*np.eye(myV.shape[0]) + myV)).rvs().reshape((-1,1))

    # "Invert"...

    L = np.linalg.cholesky(myV)
    y = np.linalg.solve(L.T,myb)

    chi2 = y.T@y

    y = pd.Series(y.squeeze(),index=myb.index)

    return chi2,1-stats.distributions.chi2.cdf(chi2,df=len(myb))

def skillings_mack(df,bootstrap=False):
    """
    Non-parametric test of correlation across columns of df.

    Algorithm from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2761045/
    """
    def construct_statistic(R,kay):
        """
        Once we have ranks, construct SM statistic
        """
        # Fill missing ranks with (k_i+1)/2
        R = R.where(~np.isnan(R),(kay+1)/2,axis=1)

        # Construct adjusted observation matrix
        A = R.subtract((kay.values+1)/2,axis=1)@np.sqrt(12/(kay.values+1))

        # Count of observations in both columns k and l
        O = ~np.isnan(X)+0.

        Sigma = np.eye(O.shape[0]) - O@O.T

        # Delete diagonal
        Sigma = Sigma - np.diag(np.diag(Sigma))

        # Add minus column sums to diagonal
        Sigma = Sigma - np.diag(Sigma.sum())

        return A.T@np.linalg.pinv(Sigma)@A

    # Drop any rows with only one column
    X = df.loc[df.count(axis=1)>0]

    n,k = X.shape

    # Counts of obs per row ("treatments")
    kay = X.count(axis=0)

    # Counts of obs per column ("blocks")
    en = X.count(axis=1)

    R = X.rank(axis=0)

    SM = construct_statistic(R,kay)

    if not bootstrap:
        p = 1-stats.distributions.chi2.cdf(SM,df=n-1)
    else:
        if bootstrap == True:
            tol = 1e-03
        else:
            tol = bootstrap

        SE = 0
        lastSE = np.inf
        its = 0
        sms = []
        while (its < 30) or (np.abs(SE-lastSE) > tol):
            lastSE = SE
            scrambled = pd.DataFrame(np.apply_along_axis(np.random.permutation,axis=0,arr=R.values),
                                     index=R.index,columns=R.columns)
           
            sms.append(construct_statistic(scrambled,kay))
            SE = np.std(sms)
            its += 1
        p = np.mean(sms>SM)

    return SM,p

friedman = skillings_mack

import pandas as pd
import numpy as np
from metrics_miscellany.estimators import ols

def randomization_inference(vars,X,y,permute_levels=None,R=None,tol=1e-3,VERBOSE=False,return_draws=False):
    """
    Return p-values associated with hypothesis that coefficients
    associated with vars are jointly equal to zero.

    Ethan Ligon                                       June 2021
    """

    assert np.all([v in X.columns for v in vars]), "vars must correspond to columns of X."

    b,V = ols(X,y)

    beta = b.squeeze()[vars]
    chi2 = chi2_test(beta,V,R=R)[0]

    last = np.inf
    p = 0
    i = 0
    Chi2 = []
    while (np.linalg.norm(p-last)>tol) or (i < 30):
        last = p
        if permute_levels is None:
            P= pd.DataFrame(np.random.permutation(X.loc[:,vars]),index=X.index,columns=vars)
        else:
            levels = X.index.names
            fixed = X.index.names.difference(permute_levels)
            P = pd.DataFrame(X.loc[:,vars].unstack(fixed).sample(frac=1).stack(fixed).values,index=X.index,columns=vars)

        myX = pd.concat([X.loc[:,X.columns.difference(vars)],P],axis=1)
        b,V = ols(myX,y)
        Chi2.append(chi2_test(b.squeeze()[vars],V,R=R)[0])
        p = (chi2<Chi2[-1])/(i+1) + last*i/(i+1)
        i += 1
        if VERBOSE: print("Latest chi2 (randomized,actual,p): (%6.2f,%6.2f,%6.4f)" % (Chi2[-1],chi2,p))

    if return_draws:
        return p,pd.Series(Chi2)
    else:
        return p

import numpy as np
from scipy.stats.distributions import chi2

def maunchy(C,N):
    """Given a sample covariance matrix C estimating using N observations,
       return p-value associated with test of whether the population
       covariance matrix is proportional to the identity matrix.
    """

    raise NotImplementedError

    m = C.shape[0]

    V = np.linalg.det(C)/((np.trace(C)/m)**m)

    rho = 1 - (2*m**2 + m + 2)/(6*m*(N-1))

    w2 = (m-1)*(m-2)*(m+2)*(2*m**3 + 6*m**2 + 3*m + 2)/(288*(m**2) * ((N-1)**2) * rho**2)

    gamma = (((N-1)*rho)**2)*w2

    x2 = -2*(N-1)*rho*np.log(V)  # Chi-squared statistic

    df = (m+2)*(m-1)/2

    px2 = chi2.cdf(x2,df)

    p = px2 + gamma/(((N-1)*rho)**2) * (chi2.cdf(x2,df+4) - px2)

    return x2,1 - px2

import numpy as np
from scipy.stats.distributions import chi2

def kr79(C,q,N):
    """Given a sample mxm covariance matrix C estimating using N observations,
       return p-value associated with test of whether the population
       covariance matrix has last q eigenvalues equal or not, where q+k=m.
    """

    m = C.shape[0]

    l = np.linalg.eigvalsh(C)  # eigenvalues in *ascending* order

    Q = (np.prod(l[:q])/(np.mean(l[:q])**q))**(N/2) # LR test statistic

    x2 = -2*np.log(Q)  # Chi-squared statistic

    df = (q-1)*(q+2)/2

    px2 = chi2.cdf(x2,df)

    #p = px2 + gamma/(((N-1)*rho)**2) * (chi2.cdf(x2,df+4) - px2)

    return x2,1 - px2

def cragg_donald(X,Q):
    """
    Cragg-Donald (1997) test for weak instruments.

    In multivariate regression

    X = Q\Pi + v

    We test null hypothesis that the rank of \Pi is less than the rank of X.

    Returns a statistic distributed chi2, along with relevant p-value
    """
    teststat = (X.T@X.resid(Q)).inv@(X.T@X.proj(Q))

    teststat = teststat.eig()[0].min()

    n,k = Q.shape

    teststat = (n-k)*teststat

    pvalue = 1 - chi2(n-X.shape[1]+1).cdf(teststat)

    return teststat,pvalue
