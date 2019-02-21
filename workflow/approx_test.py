#!/usr/bin/env python

from numba import jit
import apprentice
import numpy as np

def partialPoly(R, Punscaled, coord, denom=True):
    """
    Partial of denominator or numerator polynomial of rational approx
    by coordinate coord evaluated at (unscaled) parameter point.
    """
    import numpy as np
    structure = R._struct_q if denom else R._struct_p
    coeffs    = R._qcoeff   if denom else R._pcoeff
    P = R._scaler.scale(Punscaled)
    grad = [0] # Derivative of constant term

    if R.dim==1:
        for s in structure[1:]: # Start with the linear terms
            grad.append((s*P[0]**(s-1))/(R._scaler._Xmax[0] - R._scaler._Xmin[0])*2)

    else:
        for s in structure[1:]: # Start with the linear terms
            if s[coord] == 0: # The partial derivate evaluates to 0 if you do "d/dx of  y"
                grad.append(0)
                continue
            temp = 1.0
            for i in range(len(s)): # x,y,z,...
                if i==coord:
                    temp*=s[i]
                    temp*=P[i]**(s[i]-1)/(R._scaler._Xmax[i] - R._scaler._Xmin[i])*2 # Jacobian factor of 2/(b - a) here since we scaled into [-1,1]
                else:
                    temp*=P[i]**s[i]
            grad.append(temp)
    return np.dot(grad, coeffs)

def gradient(R, Punscaled, denom=True):
    """
    Gradeitn of denominator or numerator polynomial of rational approx
    evaluated at (unscaled) parameter point.
    """
    return [partialPoly(R, Punscaled, i, denom=denom) for i in range(R.dim)]

def denomAbsMin(rapp, box, center):
    from scipy import optimize
    return optimize.minimize(lambda x:abs(rapp.denom(x)), center, bounds=box)

def denomMin(rapp, box, center):
    from scipy import optimize
    return optimize.minimize(lambda x:rapp.denom(x), center, bounds=box)

def denomMax(rapp, box, center):
    import numpy as np
    from scipy import optimize
    return optimize.minimize(lambda x:-rapp.denom(x), center, bounds=box)

def denomMinMLSL(rapp, box, center, popsize=4, maxeval=1000):
    import numpy as np

    def my_func(x, grad):
        if grad.size > 0:
            _grad = fast_grad(x, rapp)
            for _i in range(grad.size): grad[_i] = grad[_i]
        return rapp.denom(x)

    import nlopt
    locopt = nlopt.opt(nlopt.LD_MMA, center.size)
    glopt = nlopt.opt(nlopt.GD_MLSL_LDS, center.size)
    glopt.set_min_objective(my_func)
    glopt.set_lower_bounds(np.array([b[0] for b in box]))
    glopt.set_upper_bounds(np.array([b[1] for b in box]))
    glopt.set_local_optimizer(locopt)
    glopt.set_population(popsize)
    glopt.set_maxeval(maxeval)
    xmin = glopt.optimize(center)
    return xmin

def denomMaxMLSL(rapp, box, center, popsize=10, maxeval=10000):
    import numpy as np

    def my_func(x, grad):
        if grad.size > 0:
            _grad = fast_grad(x, rapp)#gradient(rapp, x)
            for _i in range(grad.size): grad[_i] = grad[_i]
        return rapp.denom(x)

    import nlopt

    locopt = nlopt.opt(nlopt.LD_MMA, center.size)
    glopt = nlopt.opt(nlopt.GD_MLSL_LDS, center.size)
    glopt.set_max_objective(my_func)
    glopt.set_lower_bounds(np.array([b[0] for b in box]))
    glopt.set_upper_bounds(np.array([b[1] for b in box]))
    glopt.set_local_optimizer(locopt)
    glopt.set_population(popsize)
    glopt.set_maxeval(maxeval)
    xmax = glopt.optimize(center)
    return xmax


@jit
def fast_grad(x, app):
    h = 1.5e-8
    jac = np.zeros_like(x)
    f_0 = app.denom(x)
    for i in range(len(x)):
        x_d = np.copy(x)
        x_d[i] += h
        f_d = app.denom(x_d)
        jac[i] = (f_d - f_0) / h
    return jac


def denomChangesSign(rapp, box, center, popsize=4, maxeval=1000):
    # xmin_mlsl = denomMinMLSL(rapp, box, center, popsize, maxeval)
    # xmax_mlsl = denomMaxMLSL(rapp, box, center, popsize, maxeval)
    xmin = denomMin(rapp, box, center)["x"]
    xmax = denomMax(rapp, box, center)["x"]
    # DD=[rapp.Q(t) for t in rapp._scaler.drawSamples(10000)]
    bad      = rapp.denom(xmin)      * rapp.denom(xmax) <0
    if bad:
        return True, xmin, xmax
    else:
        return False, xmin, xmax

    # # bad_mlsl = rapp.denom(xmin_mlsl) * rapp.denom(xmax_mlsl) <0
    # print("std: {} mlsl: {}".format(bad, bad_mlsl))
    # if bad or bad_mlsl:
        # return True, xmin, xmax
    # else:
        # return False, xmin, xmax

def mkPlotNorm(data, f_out, norm=2):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    xi, yi, ci = [],[],[]

    for k, v in data.items():
        xi.append(k[0])
        yi.append(k[1])
        ci.append(v)

    i_winner = ci.index(min(ci))
    winner = (xi[i_winner], yi[i_winner])

    cmapname   = 'viridis'
    plt.clf()
    from matplotlib.ticker import MaxNLocator
    ax = plt.figure().gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    mpl.rc('text', usetex = True)
    mpl.rc('font', family = 'serif', size=12)
    mpl.style.use("ggplot")

    plt.scatter(winner[0], winner[1], marker = '*', c = "magenta",s=400, alpha = 0.9)
    plt.scatter(xi, yi, marker = 'o', c = np.log10(ci), cmap = cmapname, alpha = 0.8)
    plt.xlabel("$m$")
    plt.ylabel("$n$")
    plt.xlim((min(xi)-0.5,max(xi)+0.5))
    plt.ylim((min(yi)-0.5,max(yi)+0.5))
    b=plt.colorbar()
    b.set_label("$\log_{{10}}$ L{}".format(norm))

    plt.savefig(f_out)
    plt.close('all')

def mkPlotScatter(data, f_out, orders=None,lx="$x$", ly="$y$", logy=True, logx=True):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    plt.clf()
    mpl.rc('text', usetex = True)
    mpl.rc('font', family = 'serif', size=12)
    mpl.style.use("ggplot")

    plt.xlabel(lx)
    plt.ylabel(ly)
    if logx: plt.xscale("log")
    if logy: plt.yscale("log")

    txt = []

    if orders is not None:
        c   = []
        mrk = []
        for num, (m,n) in enumerate(orders):
            if n==0:
                c.append("b")
            else:
                c.append("r")
            # mrk.append(marker[clus[num]])
            txt.append("({},{})".format(m,n))
    else:
        c = ["r" for _ in len(data)]
        txt = []

    data=np.array(data)
    for num, d in enumerate(data):
        plt.scatter(d[0], d[1],c=c[num])#, marker=mrk[num])
    # plt.scatter(data[:,0], data[:,1],c=c, marker=mrk)

    if orders is not None:
        for num, t in enumerate(txt):
            plt.annotate(t, data[num])


    plt.savefig(f_out)
    plt.close('all')

def mkPlotCompromise(data, f_out, orders=None,lx="$x$", ly="$y$", logy=True, logx=True):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    plt.clf()
    mpl.rc('text', usetex = True)
    mpl.rc('font', family = 'serif', size=12)
    mpl.style.use("ggplot")


    plt.xlabel(lx)
    plt.ylabel(ly)
    if logx: plt.xscale("log")
    if logy: plt.yscale("log")

    CMP = [a*np.sqrt(b) for a,b in data]

    i_cmp = CMP.index(min(CMP))
    i_2 = CMP.index(sorted(CMP)[1])
    i_3 = CMP.index(sorted(CMP)[2])
    plt.scatter(data[i_cmp][0], data[i_cmp][1], marker = '*', c = "gold"  ,s=400, alpha = 1.0)
    plt.scatter(data[i_2][0]  , data[i_2][1]  , marker = '*', c = "silver",s=400, alpha = 1.0)
    plt.scatter(data[i_3][0]  , data[i_3][1]  , marker = '*', c = "peru"  ,s=400, alpha = 1.0)


    c, txt   = [], []
    for num, (m,n) in enumerate(orders):
        if n==0:
            c.append("b")
        else:
            c.append("r")
        txt.append("({},{})".format(m,n))

    for num, d in enumerate(data): plt.scatter(d[0], d[1],c=c[num])
    for num, t in enumerate(txt): plt.annotate(t, data[num])

    plt.savefig(f_out)
    plt.close('all')


def raNorm(ra, X, Y, norm=2):
    nrm = 0
    for num, x in enumerate(X):
        nrm+= abs(ra.predict(x) - Y[num])**norm
    return nrm

def raNormInf(ra, X, Y):
    nrm = 0
    for num, x in enumerate(X):
        nrm = max(nrm,abs(ra.predict(x) - Y[num]))
    return nrm

def mkBestRASIP(X, Y, pnames=None, train_fact=1, split=0.5, norm=2, m_max=None, n_max=None, f_plot=None, seed=1234, use_all=False):
    """
    """
    import apprentice
    np.random.seed(seed)
    _N, _dim = X.shape

    # Split dataset in training and test sample
    i_train = sorted(list(np.random.choice(range(_N), int(np.ceil(split*_N)))))
    i_test = [i for i in range(_N) if not i in i_train]

    N_train = len(i_train)
    N_test  = len(i_test)

    orders = sorted(apprentice.tools.possibleOrders(N_train, _dim, mirror=True))
    if n_max is not None: orders = [ o for o in orders if o[1] <= n_max]
    if m_max is not None: orders = [ o for o in orders if o[0] <= m_max]

    # Discard those orders where we do not have enough training points if train_fact>1
    if train_fact>1:
        _temp = []
        for o in orders:
            if o[1]>0:
                if train_fact*apprentice.tools.numCoeffsRapp(_dim, o) <= N_train:
                    _temp.append(o)
            else:
                if train_fact*apprentice.tools.numCoeffsPoly(_dim, o[0]) <= N_train:
                    _temp.append(o)
        orders = sorted(_temp)

    APP, APPcpl = [], []


    # print("Calculating {} approximations".format(len(orders)))
    import time
    t1=time.time()
    for o in orders:
        m, n = o
        if n == 0:
            i_train_o = np.random.choice(i_train, int(train_fact*apprentice.tools.numCoeffsPoly(_dim, m)))
            APP.append(apprentice.PolynomialApproximation(X[i_train_o], Y[i_train_o], order=m))
            APPcpl.append(apprentice.PolynomialApproximation(X[i_train], Y[i_train], order=m))
        else:
            i_train_o = np.random.choice(i_train, int(train_fact*apprentice.tools.numCoeffsRapp(_dim, (m,n))))
            APP.append(apprentice.RationalApproximation(X[i_train_o], Y[i_train_o], order=(m,n), strategy=1))
            APPcpl.append(apprentice.RationalApproximation(X[i_train], Y[i_train], order=(m,n), strategy=1))
        # print("I used a training size of {}/{} available training points for order {}".format(len(i_train_o), len(i_train), o))
    t2=time.time()
    print("Calculating {} approximations took {} seconds".format(len(orders), t2-t1))

    L2      = [np.sqrt(raNorm(app, X[i_test], Y[i_test],2)) for app in APP   ]
    L2cpl   = [np.sqrt(raNorm(app, X[i_test], Y[i_test],2)) for app in APPcpl]
    Linf    = [raNormInf     (app, X[i_test], Y[i_test]   ) for app in APP   ]

    # Find the order that gives the best L2 norm
    winner    = L2.index(min(L2))
    runnerup  = L2.index(sorted(L2)[1])
    winnerinf = Linf.index(min(Linf))

    o_win = orders[winner]
    o_rup = orders[runnerup]
    APP_win = APP[winner]
    APP_rup = APP[runnerup]

    # Confirm using all training data
    temp   = apprentice.RationalApproximation(X[i_train], Y[i_train], order=o_win, strategy=1)
    l2temp = np.sqrt(raNorm(temp, X[i_test], Y[i_test], 2))

    #
    print("Winner: {} with L2 {} and L2 complete = {}".format(o_win, min(L2), l2temp))
    print("Winnerinf: {} with Loo {}".format(orders[winnerinf], min(Linf)))

    for l in sorted(L2)[0:4]:
        i=L2.index(l)
        print("{} -- L2: {:10.2e} || {:10.2e} -- Loo: {:10.2e}".format(orders[i], l, L2cpl[i], Linf[i]))

    # If it is a polynomial we are done
    if o_win[1]==0: return APP_win

    # Let's check for poles in the denominator
    isbad=denomChangesSign(APP_win, APP_win._scaler.box, APP_win._scaler.center)[0]

    if isbad:

        print("Can't use this guy {} (L2: {:10.2e})".format(o_win, min(L2)))
        _l2 = min(L2)
        for l in sorted(L2)[1:]:
            i=L2.index(l)
            print("Testing {} (L2: {:10.2e})".format(orders[i], l))
            if orders[i][1]==0:
                print("This is a polynomial,done")
                return APP[i]
            else:
                bad = denomChangesSign(APP[i], APP[i]._scaler.box, APP[i]._scaler.center)[0]
                if bad:
                    ("Cannot use {} either".format(orders[i]))
                else:
                    return APP[i]
        # if rupisbad:
            # print("This guy  works though{}".format(o_rup))
        # else:
            # print("Need to fix also this guy {}".format(o_rup))

        # FS = ["filter", "scipy"]
        # FS = ["scipy"]
        # RS = ["ms"]

        # import json
        # for fs in FS:
            # for rs in RS:
                # rrr = apprentice.RationalApproximationSIP(X[i_train], Y[i_train],
                        # m=o_win[0], n=o_win[1], pnames=pnames, fitstrategy=fs, trainingscale="Cp",
                        # roboptstrategy=rs)
                # print("Test error FS {} RS {}: 1N:{} 2N:{} InfN:{}".format(fs, rs,
                                # raNorm(rrr, X[i_test], Y[i_test],1),
                                # np.sqrt(raNorm(rrr, X[i_test], Y[i_test],2)),
                                # raNormInf(rrr, X[i_test], Y[i_test])))
                # print("Total Approximation time {}\n".format(rrr.fittime))
                # print("{}".format(denomChangesSign(rrr, rrr._scaler.box, rrr._scaler.center)))

                # # with open("test2D_{}_{}.json".format(fs,rs), "w") as f: json.dump(rrr.asDict, f, indent=4)
        # return rrr

    else:
        return APP_win

def mkBestRACPL(X, Y, pnames=None, train_fact=2, split=0.6, norm=2, m_max=None, n_max=None, f_plot=None, seed=1234, allow_const=False, debug=0):
    """
    """
    import apprentice
    _N, _dim = X.shape
    np.random.seed(seed)


    # Split dataset in training and test sample
    i_train = sorted(list(np.random.choice(range(_N), int(np.ceil(split*_N)))))
    i_test = [i for i in range(_N) if not i in i_train]

    N_train = len(i_train)
    N_test  = len(i_test)

    orders = sorted(apprentice.tools.possibleOrders(N_train, _dim, mirror=True))
    if not allow_const: orders=orders[1:]
    if n_max is not None: orders = [ o for o in orders if o[1] <= n_max]
    if m_max is not None: orders = [ o for o in orders if o[0] <= m_max]

    # Discard those orders where we do not have enough training points if train_fact>1
    if train_fact>1:
        _temp = []
        for o in orders:
            if o[1]>0:
                if train_fact*apprentice.tools.numCoeffsRapp(_dim, o) <= N_train:
                    _temp.append(o)
            else:
                if train_fact*apprentice.tools.numCoeffsPoly(_dim, o[0]) <= N_train:
                    _temp.append(o)
        orders = sorted(_temp)

    APP = []

    # print("Calculating {} approximations".format(len(orders)))
    import time
    t1=time.time()
    for o in orders:
        m, n = o
        if n == 0:
            i_train_o = np.random.choice(i_train, int(train_fact*apprentice.tools.numCoeffsPoly(_dim, m)))
            APP.append(apprentice.PolynomialApproximation(X[i_train_o], Y[i_train_o], order=m, pnames=pnames))
        else:
            i_train_o = np.random.choice(i_train, int(train_fact*apprentice.tools.numCoeffsRapp(_dim, (m,n))))
            APP.append(apprentice.RationalApproximation(X[i_train_o], Y[i_train_o], order=(m,n), strategy=1, pnames=pnames))
    t2=time.time()
    print("Calculating {} approximations took {} seconds".format(len(orders), t2-t1))

    L2      = [np.sqrt(raNorm(app, X, Y, 2)) for app in APP]
    Linf    = [raNormInf(app, X, Y) for app in APP]
    NNZ     = [apprentice.tools.numNonZeroCoeff(app, 1e-6)       for app in APP]

    CMP = [a*b for a,b in zip(NNZ, L2)]

    if f_plot:
        mkPlotCompromise([(a,b) for a, b in zip(L2, NNZ)],  f_plot,  orders, lx="$L_2^\\mathrm{test}$", ly="$N_\\mathrm{non-zero}$", logy=False)

    # Proactive memory cleanup
    del APP

    for l in sorted(CMP[0:verbose]):
        i=CMP.index(l)
        oo = orders[i]
        print("{} -- L2: {:10.4e} | Loo: {:10.4e}".format(oo, L2[i], Linf[i]))

    for l in sorted(CMP):
        i=CMP.index(l)
        oo = orders[i]
        # print("{} -- L2: {:10.4e} | Loo: {:10.4e}".format(oo, L2[i], Linf[i]))
        # If it is a polynomial we are done --- return the approximation that uses all data
        if oo[1] == 0:
            return apprentice.PolynomialApproximation(X, Y, order=oo[0], pnames=pnames)
        else:
            APP_test = apprentice.RationalApproximation(X, Y, order=oo, strategy=1, pnames=pnames)
            bad = denomChangesSign(APP_test, APP_test._scaler.box, APP_test._scaler.center)[0]
            if bad:
                print("Cannot use {} due to pole in denominator".format(oo))
            else:
                return APP_test


if __name__ == "__main__":

    import os, sys, h5py
    if len(sys.argv)<3:
        print("Usage: {} input randomseed".format(sys.argv[0]))
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print("Input file '{}' not found.".format(sys.argv[1]))

    # Prevent overwriting of input data
    assert(sys.argv[2]!=sys.argv[1])

    # This reads the data
    try:
        X,Y = apprentice.tools.readData(sys.argv[1])
        app = mkBestRACPL(X, Y, m_max=5, n_max=5, pnames=None, f_plot=sys.argv[3])
    except:
        import time
        t1 = time.time()
        DATA   = apprentice.tools.readH5(sys.argv[1], [])
        idx = [i for i in range(len(DATA))]
        pnames = apprentice.tools.readPnamesH5(sys.argv[1], xfield="params")
        with h5py.File(sys.argv[1], "r") as f:
            binids = [s.decode() for s in f.get("index")[idx]]
        t2 = time.time()
        print("Data preparation took {} seconds".format(t2-t1))

        ras = []
        scl = []
        t1=time.time()
        for num, (X, Y) in  enumerate(DATA):
            t11=time.time()
            # app = mkBestRASIP(X, Y, seed=int(sys.argv[2]),m_max=5, n_max=5, split=0.7, train_fact=3)
            app = mkBestRACPL(X, Y, m_max=5, n_max=5, pnames=pnames, split=0.5, train_fact=3)#, f_plot="control_{}.pdf".format(binids[num].replace("/","_").replace("#","_")))
            # app = apprentice.PolynomialApproximation(X, Y, order=4, pnames=pnames)
            ras.append(app)#mkBestRA(X,Y, pnames, n_max=3, f_plot="{}.pdf".format(binids[num].replace("/","_"))))
            t22=time.time()
            print("Approximation {}/{} took {} seconds".format(num+1,len(binids), t22-t11))
            # ras.append(apprentice.RationalApproximation(X, Y, order=(3,0), pnames=pnames))

        t2=time.time()
        print("Approximation took {} seconds".format(t2-t1))
        # This reads the unique identifiers of the bins

        # jsonify # The decode deals with the conversion of byte string atributes to utf-8
        JD = { x : y.asDict for x, y in zip(binids, ras) }

        import json
        with open(sys.argv[2], "w") as f: json.dump(JD, f, indent=4)

        print("Done --- approximation of {} objects written to {}".format(len(idx), sys.argv[2]))
            # X, Y= DATA[0]

        # mkBestRASIP(X, Y, m_max=4, n_max=2, seed=int(sys.argv[2]) )

    # from scipy import optimize
    # r=optimize.root(lambda x:rapp.denom(x), rapp._scaler.center)
    # from IPython import embed
    # embed()
