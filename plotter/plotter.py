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
def plotSurfaceOnMap ( grid, surface, 
                      titleStr='', figFile='', clim=[0.0, 3.0]):
    """
    Plots a 2D field on top of a geographic map
    Args:
        grid    (dict)   : grid     as read by adcirc.readGrid ()
        surface (array or masked_array) : 
                   2d field as read by adcirc.readSurfaceField ()
    Optional:
        titleStr  (str)       : plot title, (''=default)
        figFile   (str)       : path for saving a figure (''=default)
        clim ([float, float]) : color limits, ([0.0, 3.0] = default)
    Returns:
        fig (matplotlib figure handle) 
    Uses:
        grid = adcirc.readGrid ('fort.14')    
        plotSurfaceOnMap (grid, grid['depth'],clim=[-100, 4000])
   #             -- will plot bathymetry on the grid.            
        maxele = adcirc.readSurfaceField ('maxele.nc', 'zeta_max' )
        plotSurfaceOnMap (grid, maxele['value'],clim=[0.0, 3.0])
   #             -- will plot maxele field on the grid.            
    """
    
    print '[info]: plotting ' + titleStr    
    lon       = grid['lon']
    lat       = grid['lat']
    triangles = grid['Elements']
    z         = surface
    Tri       = tri.Triangulation(lon, lat, triangles=triangles-1)
    
    if hasattr(z,'mask'): 
        zmask = z.mask
    else:
        zmask = np.ones(len(z), dtype=bool)
    # Set mask 
    # TODO : Optimize this following loop
    #
    mask = np.ones(len(Tri.triangles), dtype=bool)
    count = 0
    for t in Tri.triangles:
        count+=1
        ind = t
        if np.any(zmask[ind-1]):
            mask[count-1] = False    
    Tri.set_mask = mask
    
    fig = plt.figure(figsize=(9,9))    
    fig.add_axes([0.05,0.05,0.85,0.9])
    m = Basemap(llcrnrlon=min(lon), llcrnrlat=min(lat),
                urcrnrlon=max(lon), urcrnrlat=max(lat), resolution='l')
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    parallels = np.arange(-90,90,10)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=6)
    meridians = np.arange(-180,180,10)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=6)
    m.bluemarble() #m.shadedrelief()
    plt.title(titleStr)
    plt.xlabel('LONGITUDE')
    plt.ylabel('LATITUDE')
    
    myCmap = plt.cm.jet
    cs   = plt.tripcolor(Tri, z, shading='flat',\
                         edgecolors='none', \
                         vmin=clim[0], vmax=clim[1], cmap=myCmap)
    cbar = m.colorbar(cs)
    cbar.set_label('M MSL')    
    
    if len(figFile):
        try:
            plt.savefig (figFile)        
        except:
            print '[error]: cannot save figure into ' + figFile + '.'
    return fig

#==============================================================================
if __name__ == "__main__":

    grid   = adcirc.readGrid ('../adcirc/fort.14')    
    maxele = adcirc.readSurfaceField ('maxele.nc', 'zeta_max' ) 
    
    # Demo unmasked array:
    cf1 = plotSurfaceOnMap (grid, grid['depth'], titleStr='Grid Depth', 
                            figFile='hsofs.grid.depth.png', clim=[-100, 4000])
    # Demo masked array:
    cf2 = plotSurfaceOnMap (grid, maxele['value'], titleStr='Peak Flood', 
                            figFile='hsofs.maxele.png',     clim=[0.0, 3.0])
    
    
