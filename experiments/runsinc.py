
import apprentice
from apprentice import tools
import numpy as np
import os, sys

def sinc(X,dim):
    ret = 10
    for d in range(dim):
        x = X[d]
        ret *= np.sin(x)/x
    return ret

def runrapp(m,n,ts):
    fname = "f20"

    larr = [10**-6,10**-3]
    uarr = [2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"2pi",1:"4pi"}

    noisestr = ""

    folder = "%s%s_%s/sincrun"%(fname,noisestr,ts)
    if not os.path.exists(folder):
        os.mkdir(folder)

    if not os.path.exists(folder+"/benchmarkdata"):
        os.mkdir(folder+'/benchmarkdata')

    dim = 4
    numlb = 0
    numub = 1
    fndesc = "%s%s_d%d_lb%s_ub%s"%(fname,noisestr,dim,lbdesc[numlb],ubdesc[numub])
    outfile = "%s/benchmarkdata/%s.csv"%(folder,fndesc)
    fndesc = "%s%s_%s_p%d_q%d_ts%s_d%d_lb%s_ub%s"%(fname,noisestr,ts,m,n, ts, dim,lbdesc[numlb],ubdesc[numub])
    if not os.path.exists(folder+"/"+fndesc):
        os.mkdir(folder+'/'+fndesc)
    if not os.path.exists(folder+"/"+fndesc+'/outra'):
        os.mkdir(folder+'/'+fndesc+'/outra')
    if not os.path.exists(folder+"/"+fndesc+'/log/consolelogra'):
        os.makedirs(folder+'/'+fndesc+'/log/consolelogra',exist_ok = True)
    l = "_p%d_q%d_ts%s.json"%(m,n, ts)
    jsonfile = folder+'/'+fndesc+"/outra/"+fndesc+l
    consolelog = folder+'/'+fndesc+'/log/consolelogra/'+fndesc+"_p"+str(m)+"_q"+str(n)+"_ts"+ts+".log"
    cmd = 'nohup python runnonsiprapp.py %s %s %d %d %s %s >%s 2>&1 &'%(outfile,fndesc,m,n,ts,jsonfile,consolelog)
    print(cmd)
    os.system(cmd)

def runrappsip(m,n,ts):
    fname = "f20"

    larr = [10**-6,10**-3]
    uarr = [2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"2pi",1:"4pi"}
    noisestr = ""

    folder = "%s%s_%s/sincrun"%(fname,noisestr,ts)
    if not os.path.exists(folder):
        os.mkdir(folder)

    dim = 3
    numlb = 0
    numub = 1
    fndesc = "%s%s_d%d_lb%s_ub%s"%(fname,noisestr,dim,lbdesc[numlb],ubdesc[numub])
    outfile = "%s/benchmarkdata/%s.csv"%(folder,fndesc)
    fndesc = "%s%s_%s_p%d_q%d_ts%s_d%d_lb%s_ub%s"%(fname,noisestr,ts,m,n, ts, dim,lbdesc[numlb],ubdesc[numub])
    if not os.path.exists(folder+"/"+fndesc):
        os.mkdir(folder+'/'+fndesc)
    if not os.path.exists(folder+"/"+fndesc+'/out'):
        os.mkdir(folder+'/'+fndesc+'/out')
    if not os.path.exists(folder+"/"+fndesc+'/log/consolelog'):
        os.makedirs(folder+'/'+fndesc+'/log/consolelog',exist_ok = True)
    outfolder = folder+'/'+fndesc
    consolelog = folder+'/'+fndesc+'/log/consolelog/'+fndesc+"_p"+str(m)+"_q"+str(n)+"_ts"+ts+".log"
    cmd = 'nohup python runrappsip.py %s %s %d %d %s %s >%s 2>&1 &'%(outfile,fndesc,m,n,ts,outfolder,consolelog)
    print(cmd)
    os.system(cmd)


def runsinc(m,n,ts):
    fname = "f20"

    seed1 = 54321
    seed2 = 456789
    seed3 = 9876512
    seed4 = 7919820
    seed5 = 10397531
    larr = [10**-6,10**-3]
    uarr = [2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"2pi",1:"4pi"}

    seed = seed1

    noisestr = ""

    folder = "%s%s_%s/sincrun"%(fname,noisestr,ts)
    if not os.path.exists(folder):
        os.mkdir(folder)

    if not os.path.exists(folder+"/benchmarkdata"):
        os.mkdir(folder+'/benchmarkdata')

    np.random.seed(seed)


    for dim in range(2,8):
        for numlb,lb in enumerate(larr):
            for numub,ub in enumerate(uarr):
                Xperdim = ()
                for d in range(dim):
                    Xperdim = Xperdim + (np.random.rand(1000,)*(ub-lb)+lb,)

                X = np.column_stack(Xperdim)
                formatStr = "{0:0%db}"%(dim)
                for d in range(2**dim):
                    binArr = [int(x) for x in formatStr.format(d)[0:]]
                    val = []
                    for i in range(dim):
                        if(binArr[i] == 0):
                            val.append(lb)
                        else:
                            val.append(ub)
                    X[d] = val
                Y = [sinc(x,dim) for x in X]
                Y = np.atleast_2d(np.array(Y))
                fndesc = "%s%s_d%d_lb%s_ub%s"%(fname,noisestr,dim,lbdesc[numlb],ubdesc[numub])
                outfile = "%s/benchmarkdata/%s.csv"%(folder,fndesc)
                np.savetxt(outfile, np.hstack((X,Y.T)), delimiter=",")
                fndesc = "%s%s_%s_p%d_q%d_ts%s_d%d_lb%s_ub%s"%(fname,noisestr,ts,m,n, ts, dim,lbdesc[numlb],ubdesc[numub])
                if not os.path.exists(folder+"/"+fndesc):
                    os.mkdir(folder+'/'+fndesc)
                if not os.path.exists(folder+"/"+fndesc+'/out'):
                    os.mkdir(folder+'/'+fndesc+'/out')
                if not os.path.exists(folder+"/"+fndesc+'/log/consolelog'):
                    os.makedirs(folder+'/'+fndesc+'/log/consolelog',exist_ok = True)
                outfolder = folder+'/'+fndesc
                consolelog = folder+'/'+fndesc+'/log/consolelog/'+fndesc+"_p"+str(m)+"_q"+str(n)+"_ts"+ts+".log"
                cmd = 'nohup python runrappsip.py %s %s %d %d %s %s >%s 2>&1 &'%(outfile,fndesc,m,n,ts,outfolder,consolelog)
                print(cmd)
                os.system(cmd)


def createtestfiles(ts):
    fname = "f20"
    testseed =9999

    noisestr = ""
    larr = [10**-6,10**-3]
    uarr = [2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"2pi",1:"4pi"}

    folder = "%s%s_%s/sincrun"%(fname,noisestr,ts)
    if not os.path.exists(folder):
        os.mkdir(folder)

    if not os.path.exists(folder+"/benchmarkdata"):
        os.mkdir(folder+'/benchmarkdata')

    np.random.seed(testseed)
    for dim in range(2,8):
        for numlb,lb in enumerate(larr):
            for numub,ub in enumerate(uarr):
                Xperdim = ()
                for d in range(dim):
                    Xperdim = Xperdim + (np.random.rand(100000,)*(ub-lb)+lb,)

                X = np.column_stack(Xperdim)
                formatStr = "{0:0%db}"%(dim)
                for d in range(2**dim):
                    binArr = [int(x) for x in formatStr.format(d)[0:]]
                    val = []
                    for i in range(dim):
                        if(binArr[i] == 0):
                            val.append(lb)
                        else:
                            val.append(ub)
                    X[d] = val
                Y = [sinc(x,dim) for x in X]
                Y = np.atleast_2d(np.array(Y))
                fndesc = "%s%s_d%d_lb%s_ub%s"%(fname,noisestr,dim,lbdesc[numlb],ubdesc[numub])
                outfile = "%s/benchmarkdata/%s_test.csv"%(folder,fndesc)
                np.savetxt(outfile, np.hstack((X,Y.T)), delimiter=",")


def findroots(m,n,ts):
    def fn111(P,app,c1,c2,printnumer):
        x=P[0]
        y=c1
        z=c2
        # return (10.23524024435259
        # -0.6572458938123837*z
        # +2.7128389882209905*y
        # +1.5441080774930798*x
        # -6.6538979531196025*z**2
        # -0.5141146650542658*y*z
        # + 4.945747292016897y**2
        # +1.6858172869147054*x*z
        # -1.2715117330864414*x*y
        # -5.083875228303005*x**2
        # +1.400580994364511*z**3
        # -12.773709198711515*y*z**2
        # + 4.554457711154156*y**2*z
        # +6.771055260547366*y**3
        # +5.665267474305361*x*z**2
        # -1.2715117330864403*x*y*z
        # +3.4491950497063897*x*y**2
        # -2.854578456759403*x**2*z
        # +2.7757002848888925*x**2*y
        # -8.972753314590127*x**3)
        # print(x,y,z)
        X = app._scaler.scale(np.array([x,y,z]))
        if(printnumer==1):
            print("numer=%f"%(app.numer(X)))

        return app.denom(X)

    # from scipy import optimize
    # sol = optimize.root(fn, [0, 0,0],method='hybr')
    # print(sol)
    fname = "f20"

    larr = [10**-6,10**-3]
    uarr = [2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"2pi",1:"4pi"}
    m=2
    n=3
    ts="2x"

    noisestr = ""

    folder = "%s%s_%s/sincrun"%(fname,noisestr,ts)
    dim = 3
    numlb = 0
    numub = 1
    fndesc = "%s%s_%s_p%d_q%d_ts%s_d%d_lb%s_ub%s"%(fname,noisestr,ts,m,n, ts, dim,lbdesc[numlb],ubdesc[numub])
    l = "_p%d_q%d_ts%s.json"%(m,n, ts)
    jsonfile = folder+'/'+fndesc+"/out/"+fndesc+l
    if not os.path.exists(jsonfile):
        print("%s not found"%(jsonfile))
        exit(1)
    import json
    if jsonfile:
        with open(jsonfile, 'r') as fn:
            datastore = json.load(fn)
    datastore['pcoeff'] = datastore['iterationinfo'][0]['pcoeff']
    datastore['qcoeff'] = datastore['iterationinfo'][0]['qcoeff']
    from apprentice import RationalApproximationSIP
    rappsip = RationalApproximationSIP(datastore)

    X = np.linspace(larr[numlb], uarr[numub], num=1000)
    Y = np.linspace(larr[numlb], uarr[numub], num=1000)
    Z = np.linspace(larr[numlb], uarr[numub], num=1000)
    from scipy.optimize import fsolve
    x0 = 0
    for y in Y:
        for z in Z:
            x = fsolve(fn111, x0, args=(rappsip,y,z,0))
            # print(x)
            f=fn111(x,rappsip,y,z,0)
            if(f==0 and x[0]>larr[numlb] and x[0]<uarr[numub]):
                print(x,y,z,fn111(x,rappsip,y,z,1))

def getData(X_train, fn, noisepct):
    """
    TODO use eval or something to make this less noisy
    """
    from apprentice import testData
    if fn=="f1":
        Y_train = [testData.f1(x) for x in X_train]
    elif fn=="f2":
        Y_train = [testData.f2(x) for x in X_train]
    elif fn=="f3":
        Y_train = [testData.f3(x) for x in X_train]
    elif fn=="f4":
        Y_train = [testData.f4(x) for x in X_train]
    elif fn=="f5":
        Y_train = [testData.f5(x) for x in X_train]
    elif fn=="f6":
        Y_train = [testData.f6(x) for x in X_train]
    elif fn=="f7":
        Y_train = [testData.f7(x) for x in X_train]
    elif fn=="f8":
        Y_train = [testData.f8(x) for x in X_train]
    elif fn=="f9":
        Y_train = [testData.f9(x) for x in X_train]
    elif fn=="f10":
        Y_train = [testData.f10(x) for x in X_train]
    elif fn=="f12":
        Y_train = [testData.f12(x) for x in X_train]
    elif fn=="f13":
        Y_train = [testData.f13(x) for x in X_train]
    elif fn=="f14":
        Y_train = [testData.f14(x) for x in X_train]
    elif fn=="f15":
        Y_train = [testData.f15(x) for x in X_train]
    elif fn=="f16":
        Y_train = [testData.f16(x) for x in X_train]
    elif fn=="f17":
        Y_train = [testData.f17(x) for x in X_train]
    elif fn=="f18":
        Y_train = [testData.f18(x) for x in X_train]
    elif fn=="f19":
        Y_train = [testData.f19(x) for x in X_train]
    elif fn=="f20":
        Y_train = [testData.f20(x) for x in X_train]
    elif fn=="f21":
        Y_train = [testData.f21(x) for x in X_train]
    elif fn=="f22":
        Y_train = [testData.f22(x) for x in X_train]
    elif fn=="f23":
        Y_train = [testData.f23(x) for x in X_train]
    elif fn=="f24":
        Y_train = [testData.f24(x) for x in X_train]
    else:
        raise Exception("function {} not implemented, exiting".format(fn))

    stdnormalnoise = np.zeros(shape = (len(Y_train)), dtype =np.float64)
    for i in range(len(Y_train)):
        stdnormalnoise[i] = np.random.normal(0,1)
    # return Y_train
    return np.atleast_2d(np.array(Y_train)*(1+ noisepct*stdnormalnoise))

def getnoiseinfo(noise):
    noisearr = ["0","10-2","10-4","10-6"]
    noisestr = ["","_noisepct10-2","_noisepct10-4","_noisepct10-6"]
    noisepct = [0,10**-2,10**-4,10**-6]

    for i,n in enumerate(noisearr):
        if(n == noise):
            return noisestr[i],noisepct[i]

def runsincall():
    fname = "f20"

    larr = [10**-6,10**-3]
    uarr = [np.pi,2*np.pi,4*np.pi]
    lbdesc = {0:"-6",1:"-3"}
    ubdesc = {0:"pi",1:"2pi",2:"4pi"}
    noisearr = ["0","10-2","10-6"]
    dim = 4
    m = 5
    n = 5
    tstimes = 2
    ts = "2x"
    npoints = tstimes * tools.numCoeffsRapp(dim,[int(m),int(n)])
    folder = "%s_special/sincrun%d%d"%(fname,m,n)
    if not os.path.exists(folder):
        os.makedirs(folder,exist_ok = True)

    if not os.path.exists(folder+"/benchmarkdata"):
        os.makedirs(folder+"/benchmarkdata",exist_ok = True)


    for lnum,lb in enumerate(larr):
        for unum,ub in enumerate(uarr):
            minarr = []
            maxarr = []
            for d in range(dim):
                minarr.append(lb)
                maxarr.append(ub)
            # generate SG data
            from dolo.numeric.interpolation.smolyak import SmolyakGrid
            s = 0
            l = 1
            while(s<npoints):
                sg = SmolyakGrid(a=minarr,b=maxarr, l=l)
                s = sg.grid.shape[0]
                l+=1
            XatL = sg.grid
            sgm1 = SmolyakGrid(a=minarr,b=maxarr, l=(l-2))
            XatLm1 = sgm1.grid
            for noise in noisearr:
                noisestr,noisepct = getnoiseinfo(noise)
                YatL = getData(XatL, fn=fname, noisepct=noisepct)
                YatLm1 = getData(XatLm1, fn=fname, noisepct=noisepct)
                for X,Y,sample in zip([XatL,XatLm1],[YatL,YatLm1],["sgatL","sgatLm1"]):
                    outfile = "%s/benchmarkdata/%s%s_%s_l%s_u%s.csv"%(folder,fname,noisestr,sample,lbdesc[lnum],ubdesc[unum])
                    # print(outfile)
                    np.savetxt(outfile, np.hstack((X,Y.T)), delimiter=",")

            for noise in noisearr:
                noisestr,noisepct = getnoiseinfo(noise)
                for sample in ["sgatL","sgatLm1"]:
                    infile = "%s/benchmarkdata/%s%s_%s_l%s_u%s.csv"%(folder,fname,noisestr,sample,lbdesc[lnum],ubdesc[unum])
                    fndesc = "%s%s_%s_l%s_u%s_2x"%(fname,noisestr,sample,lbdesc[lnum],ubdesc[unum])
                    folderplus = folder+"/"+fndesc

                    # run rappsip
                    if not os.path.exists(folderplus + "/outrasip"):
                        os.makedirs(folderplus + "/outrasip",exist_ok = True)
                    if not os.path.exists(folderplus + "/log/consolelograsip"):
                        os.makedirs(folderplus + "/log/consolelograsip",exist_ok = True)
                    m=str(m)
                    n=str(n)
                    consolelog=folderplus + "/log/consolelograsip/"+fndesc+"_p"+m+"_q"+n+"_ts2x.log";
                    outfile = folderplus + "/outrasip/"+fndesc+"_p"+m+"_q"+n+"_ts2x.json";
                    if not os.path.exists(outfile):
                        cmd = 'nohup python runrappsip.py %s %s %s %s Cp %s %s >%s 2>&1 &'%(infile,fndesc,m,n,folderplus,outfile,consolelog)
                        # print(cmd)
                        os.system(cmd)
                        # exit(1)

                    # run rapp
                    if not os.path.exists(folderplus + "/outra"):
                        os.makedirs(folderplus + "/outra",exist_ok = True)
                    if not os.path.exists(folderplus + "/log/consolelogra"):
                        os.makedirs(folderplus + "/log/consolelogra",exist_ok = True)
                    consolelog=folderplus + "/log/consolelogra/"+fndesc+"_p"+m+"_q"+n+"_ts2x.log";
                    outfile = folderplus + "/outra/"+fndesc+"_p"+m+"_q"+n+"_ts2x.json";
                    tol = -1
                    if not os.path.exists(outfile):
                        cmd = 'nohup python runnonsiprapp.py %s %s %s %s Cp %f %s >%s 2>&1 &'%(infile,fndesc,m,n,tol,outfile,consolelog)
                        # print(cmd)
                        os.system(cmd)
                        # exit(1)

                    # run rapprd
                    if not os.path.exists(folderplus + "/outrard"):
                        os.makedirs(folderplus + "/outrard",exist_ok = True)
                    if not os.path.exists(folderplus + "/log/consolelogrard"):
                        os.makedirs(folderplus + "/log/consolelogrard",exist_ok = True)
                    consolelog=folderplus + "/log/consolelogrard/"+fndesc+"_p"+m+"_q"+n+"_ts2x.log";
                    outfile = folderplus + "/outrard/"+fndesc+"_p"+m+"_q"+n+"_ts2x.json";
                    if noise =="0":
                        tol = 10**-12
                    else:
                        noisestr,noisepct = getnoiseinfo(noise)
                        tol = noisepct * 10

                    if not os.path.exists(outfile):
                        cmd = 'nohup python runnonsiprapp.py %s %s %s %s Cp %f %s >%s 2>&1 &'%(infile,fndesc,m,n,tol,outfile,consolelog)
                        # print(cmd)
                        os.system(cmd)
                        # exit(1)







if __name__ == "__main__":

    if len(sys.argv)!=4:
        print("Usage: {} m n ts".format(sys.argv[0]))
        sys.exit(1)


    # runsinc(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3])
    # createtestfiles(sys.argv[3])
    # runrapp(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3])
    # runrappsip(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3])
    # findroots(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3])

    runsincall()
