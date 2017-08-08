# -*- coding: utf-8 -*-
from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap
import numpy as np
from OceanLab.utils import argnear
    
## Boundary condition

def BoundCond(lon,lat,lvl):
    BondCond=-1*lvl
    bat_data=Dataset('/home/helio/Data/BATHY/ETOPO/ETOPO2.nc')
    lonb=bat_data['x'][:]
    latb=bat_data['y'][:]
    bat=bat_data['z'][:]

    # Selecionado a batimetria da area de estudo
    lonBmax,lonBmin=argnear(lonb,lon.max()),argnear(lonb,lon.min())
    latBmax,latBmin=argnear(latb,lat.max()),argnear(latb,lat.min())
    lonb,latb=lonb[lonBmin:lonBmax],latb[latBmin:latBmax]
    bat=bat_data.variables['z'][latBmin:latBmax,lonBmin:lonBmax]
    LONb,LATb=np.meshgrid(lonb,latb)

    ####### Depois de importados os dados batimétricos:
    
    m = Basemap(llcrnrlon=LONb.min(),llcrnrlat=LATb.min(),urcrnrlon=LONb.max(),
 	      urcrnrlat=LATb.max(),resolution='i',projection='cyl')
    plt.ioff()
    figxinho=plt.figure()
    b=m.contour(LONb,LATb,bat,[BondCond])
    plt.close(figxinho)
    plt.ion()
    BCv=b.collections[0].get_paths()[0]
    BCv=BCv.vertices
    return BCv

def getbat(ulon,llon,ulat,llat):
    bat_data=Dataset('/home/helio/Data/BATHY/ETOPO/ETOPO2.nc')
    lonb=bat_data['x'][:]
    latb=bat_data['y'][:]
    bat=bat_data['z'][:]

    # Selecionado a batimetria da area de estudo
    lonBmax,lonBmin=argnear(lonb,ulon),argnear(lonb,llon)
    latBmax,latBmin=argnear(latb,ulat),argnear(latb,llat)
    lonb,latb=lonb[lonBmin:lonBmax],latb[latBmin:latBmax]
    bat=bat_data.variables['z'][latBmin:latBmax,lonBmin:lonBmax]
    LONb,LATb=np.meshgrid(lonb,latb)

    ####### Depois de importados os dados batimétricos:
    

    return LONb,LATb,bat