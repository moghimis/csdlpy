# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 09:57:00 2017

@author: Sergey.Vinogradov
"""
import adcirc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
from mpl_toolkits.basemap import Basemap

#==============================================================================
def plotTimeSeries ():
    print '[error]: not yet implemented'

#==============================================================================
def plotScatter ():
    print '[error]: not yet implemented'

#==============================================================================
"""
"""
def plot2DFieldOnMap ( grid, maxele, titleStr='', saveFig=None):
    
    print '[info]: plotting ' + titleStr    
    lon       = grid['lon']
    lat       = grid['lat']
    triangles = grid['Elements']
    z         = maxele['value']
    Tri       = tri.Triangulation(lon, lat, triangles=triangles-1)
    
    # Set mask 
    # TODO : Optimize this following loop
    mask = np.ones(len(Tri.triangles), dtype=bool)
    count = 0
    for t in Tri.triangles:
        count+=1
        ind = t
        if np.any(z.mask[ind-1]):
            mask[count-1] = False    
    Tri.set_mask = mask
    
    fig = plt.figure(figsize=(9,9))    
    fig.add_axes([0.1,0.1,0.8,0.8])
    m = Basemap(llcrnrlon=min(lon), llcrnrlat=min(lat),
                urcrnrlon=max(lon), urcrnrlat=max(lat), resolution='l')
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    parallels = np.arange(-90,90,10)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=6)
    meridians = np.arange(-180,180,10)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=6)
    m.shadedrelief()
    plt.title(titleStr)
    
    clim = [0, 3.0]
    myCmap = plt.cm.jet
    cs   = plt.tripcolor(Tri, z, shading='flat',\
                         edgecolors='none', \
                         vmin=clim[0], vmax=clim[1], cmap=myCmap)
    
    cbar = m.colorbar(cs)
    cbar.set_label('M MSL')
    
    if saveFig:
        plt.savefig (saveFig)        
    return fig

#==============================================================================
if __name__ == "__main__":

    maxele = \
    adcirc.read2DField ( \
    'F:/2008_Ike/NHC/hsofs.2008091106.fixed/hsofs.al092008.2008091106.nhctrk.fields.maxele.nc', \
    'zeta_max' ) 

    grid = \
    adcirc.readGrid (\
    'C:/Users/sergey.vinogradov/JET/stormsurge/mesh/CubaIkeModNOMAD1enoflux.grd')    

    print '[info]: Files are read. Now plotting...'
    cf = plot2DFieldOnMap (grid, maxele, 'hsofs.al092008.2008091106.nhctrk.fields.maxele')
    
