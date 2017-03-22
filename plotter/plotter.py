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
def plotSurfaceOnMap (grid, surface, 
                      fig=None, titleStr='', figFile='', 
                      clim=[0.0, 3.0], lonlim=None, latlim=None,
                      bar_label='M MSL', mapResolution='c'):
    """
    Plots a field specified on an unstructured grid on a geographic map
    Args:
        grid    (dict)   : grid     as read by adcirc.readGrid ()
        surface (array or masked_array) : 
                   2d field as read by adcirc.readSurfaceField ()
    Optional:
        fig (plt.figure)       : figure handle
        titleStr  (str)        : plot title, (''=default)
        figFile   (str)        : path for saving a figure (''=default)
        clim ([float, float])  : color limits, ([0.0, 3.0] = default)
        lonlim([float, float]) : longitude limits, ([min, max] = default)
        latlim([float, float]) : latitude  limits, ([min, max] = default)
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
    
    print '[info]: Plotting ' + titleStr    
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
    
    if lonlim is None:
        lonlim = [min(lon), max(lon)]
    if latlim is None:
        latlim = [min(lat), max(lat)]
    dx = lonlim[1]-lonlim[0]
    
    #Set resolution depending on longitudinal swath
    dparallels, dmeridians = 10., 10.    
    if mapResolution == 'c':
        if dx <= 50.0:
            mapResolution = 'l'
            dparallels = dmeridians = 5.0
        if dx <= 15.0:
            mapResolution = 'i'
            dparallels = dmeridians = 2.0
        if dx <=  5.0:
            mapResolution = 'h'
            dparallels = dmeridians = 1.0
        if dx <=  1.0:
            mapResolution = 'f'
            dparallels = dmeridians = 0.1
        print '[info]: Resolution is set to ' + mapResolution
               
    if fig is None:
        fig = plt.figure(figsize=(9,9))    
        
    fig.add_axes([0.05,0.05,0.85,0.9])
    m = Basemap(llcrnrlon=lonlim[0], llcrnrlat=latlim[0],
                urcrnrlon=lonlim[1], urcrnrlat=latlim[1], 
                resolution=mapResolution)
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    if dx <= 0.5:
        m.drawcounties()
    parallels = np.arange(-90,90,dparallels)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=6)
    meridians = np.arange(-180,180,dmeridians)
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
    cbar.set_label(bar_label)    
    
    if len(figFile):
        try:
            plt.savefig (figFile)        
        except:
            print '[error]: cannot save figure into ' + figFile + '.'
    
    return {'fig' : fig, 'cmap' : myCmap}

#==============================================================================
if __name__ == "__main__":

    grid   = adcirc.readGrid ('C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/adcirc/fort.14')    
    maxele = adcirc.readSurfaceField ('C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/plotter/hsofs.al092008.2008091206.nhctrk.fields.maxele.nc', \
                                      'zeta_max' ) 
    
    # Demo unmasked array:
    cf1 = plotSurfaceOnMap (grid, -1.0*grid['depth'], titleStr='Grid Depth', 
                            figFile='hsofs.grid.depth.png', clim=[-50, 10],
                            lonlim=[-75.8, -75], latlim=[35, 35.9])
    # Demo masked array:
    clim = [0.0, 3.0]
    cf = plotSurfaceOnMap (grid, maxele['value'], titleStr='Peak Flood', 
                            figFile='hsofs.maxele.png',     clim=clim,
                            lonlim=[-74.5, -71.5], latlim=[39.9, 41.6])
    
