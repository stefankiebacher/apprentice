import nlopt
import numpy as np
import sympy as sym
from apprentice import monomial
from apprentice import tools
from scipy.optimize import minimize


# from sklearn.base import BaseEstimator, RegressorMixin
# class RationalApproximationSIP(BaseEstimator, RegressorMixin):
class RationalApproximationSIP():
    def __init__(self, *args, **kwargs):
        """
        Multivariate rational approximation p(x)_m/q(x)_n

        args:
            fname   --- to read in previously calculated Pade approximation stored as the JSON file

            dict    --- to read in previously calculated Pade approximation stored as the dictionary object obtained after parsing the JSON file

            X       --- anchor points
            Y       --- function values

        kwargs:
            m               --- order of the numerator polynomial --- if omitted: auto 1 used
            n               --- order of the denominator polynomial --- if omitted: auto 1 used
            trainingscale   --- size of training data to use: 1x is the number of coeffs in numerator and denominator, 2x is twice the number of coeffecients, Cp is 100% of the data --- if omitted: auto 1x used
            box             --- box (2D array of dim X [min,max]) within which to perform the approximation --- if omitted: auto dim X [-1, 1] used
            strategy        --- strategy to use --- if omitted: auto 0 used
                                0: min ||f*p(x)_m/q(x)_n||^2_2 sub. to q(x)_n >=1
                                1: min ||f*p(x)_m/q(x)_n||^2_2 sub. to q(x)_n >=1 and some p and/or q coeffecients set to 0
                                2: min ||f*p(x)_m/q(x)_n||^2_2 + lambda*||c_pq|| sub. to q(x)_n >=1
            penaltyparam    --- lambda to use for strategy 2 --- if omitted: auto 0.1 used
            penaltybin      --- penalty binary array for numberator and denomintor of the bits to keep active in strategy 1 and put in penalty term for activity 2
                                represented in a 2D array of shape(2,(m/n)+1) where for each numberator and denominator, the bits represent penalized coeffecient degrees and constant (1: not peanlized, 0 penalized)
                                required for strategy 1 and 2

        """
        import os
        if len(args) == 0:
            pass
        else:
            if type(args[0])==dict:
                self.mkFromDict(args[0])
            elif type(args[0]) == str:
                self.mkFromJSON(args[0])
            else:
                self._X   = np.array(args[0], dtype=np.float64)
                self._Y   = np.array(args[1], dtype=np.float64)
                self.mkFromData(kwargs=kwargs)

    @property
    def dim(self): return self._dim
    @property
    def M(self): return self._M
    @property
    def N(self): return self._N
    @property
    def m(self): return self._m
    @property
    def n(self): return self._n
    @property
    def trainingscale(self): return self._trainingscale
    @property
    def trainingsize(self): return self._trainingsize
    @property
    def box(self): return self._box
    @property
    def strategy(self): return self._strategy
    @property
    def penaltyparam(self): return self._penaltyparam
    @property
    def ppenaltybin(self): return self._ppenaltybin
    @property
    def qpenaltybin(self): return self._qpenaltybin
    @property
    def pcoeff(self): return self._pcoeff
    @property
    def qcoeff(self): return self._qcoeff
    @property
    def iterationinfo(self): return self._iterationinfo

    def mkFromJSON(self, fname):
        import json
        d = json.load(open(fname))
        self.mkFromDict(d)

    def mkFromDict(self, pdict):
        self._pcoeff        = np.array(pdict["pcoeff"]).tolist()
        self._qcoeff        = np.array(pdict["qcoeff"]).tolist()
        self._iterationinfo = pdict["iterationinfo"]
        self._dim           = pdict["dim"]
        self._m             = pdict["m"]
        self._n             = pdict["n"]
        self._M             = pdict["M"]
        self._N             = pdict["N"]
        self._strategy      = pdict["strategy"]
        self._box           = np.array(pdict["box"],dtype=np.float64)
        self._trainingscale = pdict["trainingscale"]
        self._trainingsize  = pdict["trainingsize"]
        self._penaltyparam  = 0.0

        if(self.strategy ==1 or self.strategy==2):
            self._ppenaltybin = pdict['chosenppenalty']
            self._qpenaltybin = pdict['chosenqpenalty']

        if(self.strategy == 2):
            self._penaltyparam = pdict['lambda']
        # self.setStructures(pdict["m"], pdict["n"])

    def mkFromData(self, kwargs):
        """
        Calculate the Pade approximation
        """
        # order=kwargs["order"]
        # debug=kwargs["debug"] if kwargs.get("debug") is not None else False
        # strategy=int(kwargs["strategy"]) if kwargs.get("strategy") is not None else 2
        # self.fit(order[0], order[1], debug=debug, strategy=strategy)

        self._dim           = self._X[0].shape[0]

        self._m             = int(kwargs["m"]) if kwargs.get("m") is not None else 1
        self._n             = int(kwargs["n"]) if kwargs.get("n") is not None else 1
        self._M             = tools.numCoeffsPoly(self.dim, self.m)
        self._N             = tools.numCoeffsPoly(self.dim, self.n)
        self._strategy      = int(kwargs["strategy"]) if kwargs.get("strategy") is not None else 0
        self._box           = np.empty(shape=(0,2))

        if(kwargs.get("box") is not None):
            for arr in kwargs.get("box"):
                newArr =np.array([[arr[0],arr[1]]],dtype=np.float64)
                self._box = np.concatenate((self._box,newArr),axis=0)
        else:
            for i in range(self.dim):
                newArr = np.array([[-1,1]],dtype=np.float64)
                self._box = np.concatenate((self._box,newArr),axis=0)

        self._trainingscale = kwargs["trainingscale"] if kwargs.get("trainingscale") is not None else "1x"
        if(self.trainingscale == "1x"):
            self._trainingsize = self.M+self.N
        elif(self.trainingscale == "2x"):
            self._trainingsize = 2*(self.M+self.N)
        elif(self.trainingscale == "Cp"):
            self._trainingsize = len(self.X)

        self._penaltyparam  = kwargs["penaltyparam"] if kwargs.get("penaltyparam") is not None else 0.0

        if(kwargs.get("ppenaltybin") is not None):
            self._ppenaltybin = kwargs["ppenaltybin"]
        elif(self.strategy ==1 or self.strategy==2):
            raise Exception("Binary Penalty for numerator required for strategy 1 and 2")

        if(kwargs.get("qpenaltybin") is not None):
            self._qpenaltybin = kwargs["qpenaltybin"]
        elif(self.strategy ==1 or self.strategy==2):
            raise Exception("Binary Penalty for denomintor equired for strategy 1 and 2")


        self._struct_p      = monomial.monomialStructure(self.dim, self.m)
        self._struct_q      = monomial.monomialStructure(self.dim, self.n)

        self._ipo            = np.empty((self.trainingsize,2),"object")
        for i in range(self.trainingsize):
            self._ipo[i][0] = monomial.recurrence(self._X[i,:],self._struct_p)
            self._ipo[i][1]= monomial.recurrence(self._X[i,:],self._struct_q)
        self.fit()

    def fit(self):
        # Strategies:
        # 0: LSQ with SIP and without penalty
        # 1: LSQ with SIP and some coeffs set to 0 (using constraints)
        # 2: LSQ with SIP, penaltyParam > 0 and all or some coeffs in L1 term


        cons = np.empty(self.trainingsize, "object")
        for trainingIndex in range(self.trainingsize):
            q_ipo = self._ipo[trainingIndex][1]
            cons[trainingIndex] = {'type': 'ineq', 'fun':self.robustSample, 'args':(q_ipo,)}

        p_penaltyIndex = []
        q_penaltyIndex = []
        if(self.strategy ==1 or self.strategy == 2):
            p_penaltyIndex, q_penaltyIndex = self.createPenaltyIndexArr()
        coeff0 = []
        if(self.strategy == 0):
            coeffs0 = np.zeros((self.M+self.N))
        elif(self.strategy == 1):
            coeffs0 = np.zeros((self.M+self.N))
            for index in p_penaltyIndex:
                cons = np.append(cons,{'type': 'eq', 'fun':self.coeffSetTo0, 'args':(index, "p")})
            for index in q_penaltyIndex:
                cons = np.append(cons,{'type': 'eq', 'fun':self.coeffSetTo0, 'args':(index, "q")})
        elif(self.strategy == 2):
            coeffs0 = np.zeros(2*(self.M+self.N))
            for index in p_penaltyIndex:
                cons = np.append(cons,{'type': 'ineq', 'fun':self.abs1, 'args':(index, "p")})
                cons = np.append(cons,{'type': 'ineq', 'fun':self.abs2, 'args':(index, "p")})
            for index in q_penaltyIndex:
                cons = np.append(cons,{'type': 'ineq', 'fun':self.abs1, 'args':(index, "q")})
                cons = np.append(cons,{'type': 'ineq', 'fun':self.abs2, 'args':(index, "q")})
        else:
            raise Exception("fit() strategy %i not implemented"%self.strategy)

        maxIterations = 100 # hardcode for now. Param later?
        self._iterationinfo = []
        for iter in range(1,maxIterations+1):
            data = {}
            data['iterationNo'] = iter
            ret = {}
            if(self.strategy == 2):
                ret = minimize(self.leastSqObjWithPenalty, coeffs0, args = (p_penaltyIndex,q_penaltyIndex),method = 'SLSQP', constraints=cons, options={'iprint': 0,'ftol': 1e-6, 'disp': False})
            else:
                ret = minimize(self.leastSqObj, coeffs0 ,method = 'SLSQP', constraints=cons, options={'iprint': 0,'ftol': 1e-6, 'disp': False})
            coeffs = ret.get('x')
            leastSq = ret.get('fun')
            data['leastSqObj'] = leastSq
            data['pcoeff'] = coeffs[0:self.M].tolist()
            data['qcoeff'] = coeffs[self.M:self.M+self.N].tolist()

            if(self.strategy == 2):
                lsqsplit = {}
                l1term = self.computel1Term(coeffs,p_penaltyIndex,q_penaltyIndex)
                lsqsplit['l1term'] = l1term
                lsqsplit['l2term'] = leastSq - l1term
                data['leastSqSplit'] = lsqsplit


            x0 = np.array([(self.box[i][0]+self.box[i][1])/2 for i in range(self.dim)], dtype=np.float64)

            ret = minimize(self.robustObj, x0, bounds=self.box, args = (coeffs,),method = 'L-BFGS-B')
            x = ret.get('x')
            robO = ret.get('fun')
            data['robustArg'] = x.tolist()
            data['robustObj'] = robO
            self._iterationinfo.append(data)
            if(robO >= 0.02):
                break
            q_ipo_new = monomial.recurrence(x,self._struct_q)
            cons = np.append(cons,{'type': 'ineq', 'fun':self.robustSample, 'args':(q_ipo_new,)})

        if(len(self._iterationinfo) == maxIterations and self._iterationinfo[maxIterations-1]["robustObj"]<0.02):
            raise Exception("Could not find a robust objective")
        self._pcoeff = self._iterationinfo[len(self._iterationinfo)-1]["pcoeff"]
        self._qcoeff = self._iterationinfo[len(self._iterationinfo)-1]["qcoeff"]


    def leastSqObj(self,coeff):
        sum = 0
        for index in range(self.trainingsize):
            p_ipo = self._ipo[index][0]
            q_ipo = self._ipo[index][1]

            P = np.sum([coeff[i]*p_ipo[i] for i in range(self.M)])
            Q = np.sum([coeff[i]*q_ipo[i-self.M] for i in range(self.M,self.M+self.N)])

            sum += (self._Y[index] * Q - P)**2
        return sum

    def computel1Term(self,coeff,p_penaltyIndexs=np.array([]), q_penaltyIndexs=np.array([])):
        l1Term = 0
        for index in p_penaltyIndexs:
            l1Term += self.penaltyparam * coeff[self.M+self.N+index]
        for index in q_penaltyIndexs:
            l1Term += self.penaltyparam * coeff[self.M+self.N+self.M+index]
        return l1Term

    def leastSqObjWithPenalty(self,coeff,p_penaltyIndexs=np.array([]), q_penaltyIndexs=np.array([])):
        sum = self.leastSqObj(coeff)
        l1Term = self.computel1Term(coeff, p_penaltyIndexs, q_penaltyIndexs)
        return sum+l1Term

    def abs1(self,coeff, index, pOrq="q"):
        ret = -1
        if(pOrq == "p"):
            ret = coeff[self.M+self.N+index] - coeff[index]
        elif(pOrq == "q"):
            ret = coeff[self.M+self.N+self.M+index] - coeff[self.M+index]
        return ret

    def abs2(self,coeff, index, pOrq="q"):
        ret = -1
        if(pOrq == "p"):
            ret = coeff[self.M+self.N+index] + coeff[index]
        elif(pOrq == "q"):
            ret = coeff[self.M+self.N+self.M+index] + coeff[self.M+index]
        return ret

    def coeffSetTo0(self, coeff, index, pOrq="q"):
        ret = -1
        if(pOrq == "p"):
            ret = coeff[index]
        elif(pOrq == "q"):
            ret = coeff[self.M+index]
        return ret

    def robustSample(self,coeff, q_ipo):
        return np.sum([coeff[i]*q_ipo[i-self.M] for i in range(self.M,self.M+self.N)])-1

    def robustObj(self,x,coeff):
        q_ipo = monomial.recurrence(x,self._struct_q)
        return np.sum([coeff[i]*q_ipo[i-self.M] for i in range(self.M,self.M+self.N)])

    def createPenaltyIndexArr(self):
        p_penaltyBinArr = self.ppenaltybin
        q_penaltyBinArr = self.qpenaltybin

        p_penaltyIndex = np.array([], dtype=np.int64)
        for index in range(self.m+1):
            if(p_penaltyBinArr[index] == 0):
                if(index == 0):
                    p_penaltyIndex = np.append(p_penaltyIndex, 0)
                else:
                    A = tools.numCoeffsPoly(self.dim, index-1)
                    B = tools.numCoeffsPoly(self.dim, index)
                    for i in range(A, B):
                        p_penaltyIndex = np.append(p_penaltyIndex, i)

        q_penaltyIndex = np.array([],dtype=np.int64)
        for index in range(self.n+1):
            if(q_penaltyBinArr[index] == 0):
                if(q_penaltyBinArr[index] == 0):
                    if(index == 0):
                        q_penaltyIndex = np.append(q_penaltyIndex, 0)
                    else:
                        A = tools.numCoeffsPoly(self.dim, index-1)
                        B = tools.numCoeffsPoly(self.dim, index)
                        for i in range(A, B):
                            q_penaltyIndex = np.append(q_penaltyIndex, i)

        return p_penaltyIndex, q_penaltyIndex

    @property
    def asDict(self):
        """
        Store all info in dict as basic python objects suitable for JSON
        """
        d={}
        d['pcoeff']                 = self._pcoeff
        d['qcoeff']                 = self._qcoeff
        d['iterationinfo']    = self._iterationinfo
        d['dim']              = self._dim
        d['m'] = self._m
        d['n'] = self._n
        d['M'] = self._M
        d['N'] = self._N
        d['strategy'] = self._strategy
        d['box'] = self._box.tolist()
        d['trainingscale'] = self._trainingscale
        d['trainingsize'] = self._trainingsize

        if(self.strategy ==1 or self.strategy==2):
            d['chosenppenalty'] = self._ppenaltybin
            d['chosenqpenalty'] = self._qpenaltybin


        if(self.strategy==2):
            d['lambda'] = self._penaltyparam
        return d

    @property
    def asJSON(self):
        """
        Store all info in dict as basic python objects suitable for JSON
        """
        d = self.asDict
        import json
        return json.dumps(d,indent=4, sort_keys=True)

    def save(self, fname, indent=4, sort_keys=True):
        import json
        with open(fname, "w") as f:
            json.dump(self.asDict, f,indent=indent, sort_keys=sort_keys)

if __name__=="__main__":
    import sys
    infilePath = "/Users/mkrishnamoorthy/Research/Code/apprentice/benchmarkdata/f11_noise_0.1.txt"
    X, Y = tools.readData(infilePath)
    r = RationalApproximationSIP(X,Y,
                                m=2,
                                n=3,
                                trainingscale="1x",
                                box=np.array([[-1,1]]),
                                strategy=2,
                                penaltyparam=10**-1,
                                ppenaltybin=[1,0,0],
                                qpenaltybin=[1,0,0,0]
    )
    # r.save("/Users/mkrishnamoorthy/Desktop/pythonRASIP.json")

    r2 = RationalApproximationSIP(r.asDict)
    print(r2.asJSON)

    # r1 = RationalApproximationSIP("/Users/mkrishnamoorthy/Desktop/pythonRASIP.json")
    # print(r1.asJSON)








# END
