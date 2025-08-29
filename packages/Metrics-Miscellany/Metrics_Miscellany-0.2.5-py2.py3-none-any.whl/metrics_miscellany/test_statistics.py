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
