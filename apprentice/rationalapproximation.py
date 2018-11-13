import numpy as np

#https://medium.com/pythonhive/python-decorator-to-measure-the-execution-time-of-methods-fa04cb6bb36d
def timeit(method):
    import time
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed

from sklearn.base import BaseEstimator, RegressorMixin
class RationalApproximation(BaseEstimator, RegressorMixin):
    def __init__(self, X=None, Y=None, order=(2,1), fname=None, initDict=None, strategy=2):
        """
        Multivariate rational approximation f(x)_mn =  g(x)_m/h(x)_n

        kwargs:
            fname --- to read in previously calculated Pade approximation

            X     --- anchor points
            Y     --- function values
            order --- tuple (m,n) m being the order of the numerator polynomial --- if omitted: auto
        """
        if initDict is not None:
            self.mkFromDict(initDict)
        elif fname is not None:
            self.mkFromJSON(fname)
        elif X is not None and Y is not None:
            self._m=order[0]
            self._n=order[1]
            self._X   = np.array(X, dtype=np.float64)
            self._dim = self._X[0].shape[0]
            self._Y   = np.array(Y, dtype=np.float64)
            self._trainingsize=len(X)
            self.fit(strategy=strategy)
        else:
            raise Exception("Constructor not called correctly, use either fname, initDict or X and Y")

    @property
    def dim(self): return self._dim
    @property
    def trainingsize(self): return self._trainingsize
    @property
    def M(self): return self._M
    @property
    def N(self): return self._N
    @property
    def m(self): return self._m
    @property
    def n(self): return self._n

    def setStructures(self):
        from apprentice import monomial
        self._struct_p = monomial.monomialStructure(self.dim, self.m)
        self._struct_q = monomial.monomialStructure(self.dim, self.n)
        from apprentice import tools
        self._M        = tools.numCoeffsPoly(self.dim, self.m)
        self._N        = tools.numCoeffsPoly(self.dim, self.n)
        self._K = 1 + self._m + self._n

    # @timeit
    def coeffSolve(self, VM, VN):
        """
        This does the solving for the numerator and denominator coefficients
        following Anthony's recipe.
        """
        Fmatrix=np.diag(self._Y)
        # rcond changes from 1.13 to 1.14
        rcond = -1 if np.version.version < "1.15" else None
        MM, res, rank, s  = np.linalg.lstsq(VM, Fmatrix, rcond=rcond)
        Zmatrix = MM.dot(VN)
        U, S, V = np.linalg.svd(VM.dot(Zmatrix) - Fmatrix.dot(VN))
        self._qcoeff = V[-1]
        self._pcoeff = Zmatrix.dot(self._qcoeff)

    # @timeit
    def coeffSolve2(self, VM, VN):
        """
        This does the solving for the numerator and denominator coefficients
        following Steve's recipe.
        """
        Feps = - (VN.T * self._Y).T
        # the full left side of the equation
        y = np.hstack([ VM, Feps[:,1:self._Y.size ] ])
        U, S, V = np.linalg.svd(y)
        # manipulations to solve for the coefficients
        # Given A = U Sigma VT, for A x = b, x = V Sigma^-1 UT b
        tmp1 = np.transpose( U ).dot( np.transpose( self._Y ))[0:S.size]
        Sinv = np.linalg.inv( np.diag(S) )
        x = np.transpose(V).dot( Sinv.dot(tmp1) )
        self._pcoeff = x[0:self._M]
        self._qcoeff = np.concatenate([np.array([1.00]),x[self._M:self._M+self._N+1]])

    def fit(self, **kwargs):
        """
        Do everything
        """
        # Set M, N, K, polynomial structures
        # n_required=self.numCoeffs(self.dim, m+n+1)
        from apprentice import tools
        n_required = tools.numCoeffsRapp(self.dim, (self.m, self.n))
        if n_required > self._Y.shape[0]:
            raise Exception("Not enough inputs: got %i but require %i to do m=%i n=%i"%(n_required, Fmatrix.shape[0], m,n))

        self.setStructures()

        from apprentice import monomial
        VanderMonde=monomial.vandermonde(self._X, self._K)
        VM = VanderMonde[:, 0:(self._M)]
        VN = VanderMonde[:, 0:(self._N)]
        strategy=kwargs["strategy"] if kwargs.get("strategy") is not None else 2
        if   strategy==1: self.coeffSolve( VM, VN)
        elif strategy==2: self.coeffSolve2(VM, VN)
        else: raise Exception("fit() strategy %i not implemented"%strategy)

    def Q(self, X):
        """
        Evaluation of the denom poly at X.
        """
        from apprentice import monomial
        rec_q = np.array(monomial.recurrence(X, self._struct_q))
        q = self._qcoeff.dot(rec_q)
        return q

    def P(self, X):
        """
        Evaluation of the numer poly at X.
        """
        from apprentice import monomial
        rec_p = np.array(monomial.recurrence(X, self._struct_p))
        p = self._pcoeff.dot(rec_p)
        return p

    def predict(self, X):
        """
        Return the prediction of the RationalApproximation at X.
        """
        X=np.array(X)
        return self.P(X)/self.Q(X)

    def __call__(self, X):
        """
        Operator version of predict.
        """
        return self.predict(X)

    def __repr__(self):
        """
        Print-friendly representation.
        """
        return "<RationalApproximation dim:{} m:{} n:{}>".format(self.dim, self.m, self.n)

    @property
    def asDict(self):
        """
        Store all info in dict as basic python objects suitable for JSON
        """
        d={}
        d["dim"]    = self.dim
        d["trainingsize"] = self.trainingsize
        d["m"]      = self.m
        d["n"]      = self.n
        d["pcoeff"] = list(self._pcoeff)
        d["qcoeff"] = list(self._qcoeff)
        return d

    def save(self, fname):
        import json
        with open(fname, "w") as f:
            json.dump(self.asDict, f)

    def mkFromDict(self, pdict):
        self._pcoeff = np.array(pdict["pcoeff"])
        self._qcoeff = np.array(pdict["qcoeff"])
        self._m      = int(pdict["m"])
        self._n      = int(pdict["n"])
        self._dim    = int(pdict["dim"])
        try:
            self._trainingsize = int(pdict["trainingsize"])
        except:
            pass
        self.setStructures()

    def mkFromJSON(self, fname):
        import json
        d = json.load(open(fname))
        self.mkFromDict(d)

if __name__=="__main__":

    import sys

    def mkTestData(NX, dim=1):
        def anthonyFunc(x):
            return (10*x)/(x**3 - 4* x + 5)
        NR = 1
        np.random.seed(555)
        X = np.random.rand(NX, dim)
        Y = np.array([anthonyFunc(*x) for x in X])
        return X, Y

    X, Y = mkTestData(500)
    r=RationalApproximation(X=X,Y=Y, order=(1,3))
    r.save("testrational.json")
    r=RationalApproximation(fname="testrational.json")

    import pylab
    pylab.plot(X, Y, marker="*", linestyle="none", label="Data")
    TX = sorted(X)
    YW = [r(p) for p in TX]

    pylab.plot(TX, YW, label="Rational approx m={} n={}".format(1,3))
    pylab.legend()
    pylab.xlabel("x")
    pylab.ylabel("f(x)")
    pylab.savefig("demo.pdf")

    sys.exit(0)
