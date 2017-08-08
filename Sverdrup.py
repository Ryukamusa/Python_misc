import scipy.interpolate as scint
import numpy as np
import matplotlib.path as Pt
import matplotlib.pyplot as plt

def transport(V,d,z,velpos='None',sigrad='None'):
    pts=[]
    D,Z=np.meshgrid(d,z)
    plt.figure(figsize=(15,8))
    val=np.nanmax(np.abs(V))
    lv=np.linspace(-val,val,80,endpoint=True)
    ctf=plt.contourf(D,Z,V,lv,cmap='seismic_r')
    ct=plt.contour(D,Z,V,10,colors='w')
    plt.clabel(ct,fmt='%2f')
    if sigrad != 'None':
        plt.plot(d,sigrad*-1.,'--g',linewidth=2)
    elif velpos != 'None':
        plt.contour(D,Z,V,[-1*velpos,velpos],colors='g')
    suplim=np.abs(np.min(z)*0.05)
    plt.colorbar(ctf)
    plt.ylim(z.min(),suplim)
    pts=np.array(plt.ginput(0,0))
    if pts != []:
        plt.close()
    dp,zp=pts[:,0],pts[:,1]
    PTS=Pt.Path(pts)
    posits=np.array([D.ravel(),Z.ravel()]).T
    cond=PTS.contains_points(posits)
    cond=cond.reshape(D.shape)
    Vn=V.copy()
    Vn[~cond]=np.nan
    condD=np.argwhere((d>=dp.min())&(d<=dp.max())).T[0]
    condZ=np.argwhere((z>=zp.min())&(z<=zp.max())).T[0]
    zn=z[condZ[0]:condZ[-1]+1]
    dn=d[condD[0]:condD[-1]+1]
    vn=Vn[condZ[0]:condZ[-1]+1,condD[0]:condD[-1]+1]
    Dp,Zp=np.meshgrid(dn,zn)
    plt.figure(figsize=(15,8))
    val=np.nanmax(np.abs(vn))
    lv=np.linspace(-val,val,80,endpoint=True)
    ctf=plt.contourf(Dp,Zp,vn,lv,cmap='seismic_r')
    plt.contour(Dp,Zp,vn,[-1*velpos,velpos],colors='g')
    if (np.any(np.diff(zn)!=np.diff(zn)[0]))|(np.any(np.diff(dn)!=np.diff(dn)[0])):
        #gera vetor z de 1 em 1 m
        zN=np.arange(zn[0],zn[-1]-1,-1)
        dN=np.arange(dn[0],dn[-1]+1,+1)
        Dn,Zn=np.meshgrid(dN,zN)
        ##retira os nans para interpolar
        Dp,Zp=Dp[~np.isnan(vn)],Zp[~np.isnan(vn)]
        vn=vn[~np.isnan(vn)]
        Vcalc=scint.griddata((Dp,Zp),vn,(Dn.ravel(),Zn.ravel()),method='linear')
        Vcalc=Vcalc.reshape(Dn.shape)
        Ag=1e3
    else:
        Dn,Zn=Dp,Zp
        Vcalc=vn
        Ag=np.diff(zn)[0]*np.diff(dn)*1e3
    if np.nanmedian(Vcalc)<0:
        calc=Vcalc[Vcalc<-1.*velpos]
        calsup=Vcalc[0,:]
        calsup=calsup[calsup<-1.*velpos]
    elif np.nanmedian(Vcalc)>0:
        calc=Vcalc[Vcalc>velpos]
        calsup=Vcalc[0,:]
        calsup=calsup[calsup>velpos]
    Sv=(np.sum(calc)*Ag)*1e-6
    return Sv,pts,np.sum(calsup)