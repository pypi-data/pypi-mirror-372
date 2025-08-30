import datetime
import numpy as np
import scipy.optimize
#https://github.com/scipy/scipy/issues/19441#issuecomment-1783203946 mvn is technically not supported
from scipy.stats import _mvn
from functools import lru_cache
import math

eps_factor = 1E6 * np.finfo(np.dtype('float64')).eps
quantiles = np.array([0, np.inf], dtype=float)
lower = np.array([-np.inf, -np.inf], dtype=float)
maxpts = 2000000
abseps = 1e-5
releps = 1e-5
sqrt2 = np.sqrt(2)
@lru_cache


#Function to make a log cdf given means and covariance values of two sentences
def logcdf(m1, m2, c1, c2):
    cd = (c1 + c2) / 2.0
    #if c1*c2 < cd*eps_factor:
    #    raise ValueError('singular matrix')
    cod = (c1 - c2) / 2.0
    cov = [[cd, cod], [cod, cd]]
    mean = [(m1-m2)/sqrt2, (m1+m2)/sqrt2]
    return math.log(_mvn.mvnun(lower, quantiles, mean, cov, maxpts, abseps, releps)[0])

#Function to make a means and covariance matrix to be used to generate a list of the best sentence to compare
#accepts a list of comparisons and a list of sentences
def mle(comparisons, sentences):
    N = len(sentences)
    sbym = {}
    #comparisons = [[int(c.split(",")[0]), int(c.split(",")[1])] for c in comparisons]
    def objective(x, comparisons):
        means = x[:N]
        cov = x[N:]
        #
        try:
            c_hat = -sum(logcdf(means[a], means[b], cov[a], cov[b]) for a, b in comparisons)
            #print(c_hat)
            return(c_hat)
        except Exception as e:
            print(e)
            return -np.inf

    dt = datetime.datetime.now()
    print("starting base at %s" % dt)
    res = scipy.optimize.minimize(
        objective,
        np.concatenate((np.zeros(N), np.full(N, 1))),
        args=(comparisons[:-1],),
        options={"ftol":1e-10},
        bounds=scipy.optimize.Bounds(
            lb=0,
            ub=np.inf
        )
    )
    #this is the mean and covariance matrix
    #return best_rankings(res.x[:N], np.diag(res.x[N:]))
    m, c = res.x[:N], np.diag(res.x[N:])
    for sentence in sentences:
        sbym[sentence] = m[sentences.index(sentence)]
    sbym_sorted = sorted(sbym.items(), key=lambda item: item[1])
    return sbym_sorted, m, c

def best_rankings(m, x):
    relevance = []
    #i is one sentence id in the data
    for i in range(len(m)):
        for j in range(i+1, len(m)):
            #averages of sentences are at the corresponding index in the list m
            mi= m[i]
            mj = m[j]
            #covariance value is at the crossover of i and j in the covariance matrix
            cii = x[i][i]
            cjj = x[j][j]
            #xbox function with the above variables for i and j
            a = (mi - (2*cii))
            b = (mi + (2*cii))
            c = (mj - (2*cjj))
            d = (mj + (2*cjj))
            p1 = (np.minimum(b, d) - np.maximum(a,c)) / (np.maximum(b, d) - np.minimum(a, c))
            p2 = max((b-a), (d-c))
            res = p1*p2
            #append the value of the relevance along with the sentence ids
            relevance.append([res, i, j])
        relevance = sorted(relevance, key=lambda x: x[0], reverse=False)
    return relevance

