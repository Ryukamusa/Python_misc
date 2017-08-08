import matplotlib.pyplot as plt
import numpy as np
import seawater as sw

def wkb(N2,f,nmodes=3):
    Nb=np.nanmean(N2)
    P=np.arange(0.,N2.size)
    P0=np.ones(N2.size)
    plt.figure()
    rdi=np.zeros(nmodes)
    for n in np.arange(1,nmodes):
        P[0]=(-1)**n*np.sqrt(2*N2[0]/Nb)
        P[-1]=np.sqrt(2*N2[-1]/Nb)
        rdi[n]=np.abs((n*np.pi*f/(Nb*N2.size-1)))
        for z in np.arange(1,N2.size):
            P[z]=np.sqrt(2*N2[z]/Nb)*np.cos(n*np.pi/(Nb*N2.size-1)*np.sum(N2[z:]))
        plt.plot(np.flipud(P),-np.arange(0,N2.size),linewidth=1.6)
    plt.plot(np.flipud(P0),-np.arange(0,N2.size),linewidth=1.6)
    plt.plot(np.tile(0,N2.size),-np.arange(0,N2.size),'--k',linewidth=1.6)
    
    return rdi


prof_max=5000.
z=np.arange(0.,prof_max+1)*-1
d=900.
f=sw.f(23.)

N2=10**4*np.exp(z/d)*f**2
#N2=np.ones(z.size)*5
plt.figure()
plt.plot(N2,z)

rdi=wkb(N2,f,nmodes=3)



    