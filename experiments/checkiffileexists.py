import numpy as np
from apprentice import RationalApproximationSIP, RationalApproximationONB, PolynomialApproximation
from apprentice import tools, readData
import matplotlib.ticker as mtick
import os

def getfarr():
    farr = ["f1","f2","f3","f4","f5","f7","f8","f9","f10","f12","f13","f14","f15","f16",
            "f17","f18","f19","f20","f21","f22"]
    # farr = ["f1","f2","f3","f4","f5","f7","f8","f9","f10","f12","f13","f14","f15","f16",
    #         "f17","f18","f19","f21","f22"]
    # farr = ["f20"]

    return farr

def getnoiseinfo(noise):
    noisearr = ["0","10-2","10-4","10-6"]
    noisestr = ["","_noisepct10-2","_noisepct10-4","_noisepct10-6"]
    noisepct = [0,10**-2,10**-4,10**-6]

    for i,n in enumerate(noisearr):
        if(n == noise):
            return noisestr[i],noisepct[i]

def check():
    noiselevels = ['0','10-2','10-6']
    allsamples = ['mc','lhs','so','sg']
    # allsamples = ['mc','lhs']
    # allsamples = ['sg']
    fff = getfarr()
    for snum,sample in enumerate(allsamples):
        for nnum,noise in enumerate(noiselevels):
            noisestr,noisepct = getnoiseinfo(noise)
            for fnum,fname in enumerate(fff):
                ts = "2x"

                for run in ["exp1","exp2","exp3","exp4","exp5"]:
                    fndesc = "%s%s_%s_%s"%(fname,noisestr,sample,ts)
                    folder = "results/%s/%s"%(run,fndesc)
                    m = 5
                    n = 5
                    pq = "p%d_q%d"%(m,n)
                    # print(run, fname,noisestr,sample,m,n)

                    rappsipfile = "%s/outrasip/%s_%s_ts%s.json"%(folder,fndesc,pq,ts)
                    rappfile = "%s/outra/%s_%s_ts%s.json"%(folder,fndesc,pq,ts)
                    rapprdfile = "%s/outrard/%s_%s_ts%s.json"%(folder,fndesc,pq,ts)
                    pappfile = "%s/outpa/%s_%s_ts%s.json"%(folder,fndesc,pq,ts)
                    if not os.path.exists(rappsipfile):
                        print("rappsipfile %s not found\n"%(rappsipfile))


                    if not os.path.exists(rappfile):
                        print("rappfile %s not found\n"%(rappfile))


                    if not os.path.exists(rapprdfile):
                        print("rappfile %s not found\n"%(rapprdfile))


                    if not os.path.exists(pappfile):
                        print("pappfile %s not found\n"%(pappfile))



                    if(sample == "sg"):
                        break

                 
if __name__ == "__main__":

    check()
 ###########