# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 10:45:00 2017

@author: Sergey.Vinogradov
"""
import adcirc
from obs.coops import readLonLatVal
import numpy as np
from scipy.interpolate import griddata
import copy

#==============================================================================
def interpCoastal (grid, data, isobathToTaper = 200.):
    """
    Interpolates sparse near-coastal data onto a specified unstructured grid
    with tapering the interpolated values to zero at and below a specified
    isobath. 
    Args:
        grid                         :  as read by csdlpy.adcirc.readGrid()
        data ([float, float, float]) :  lon, lat, value
    Optional:
        isobathToTaper (float)       : (default=200.), depth below which
                                       the result tapers to 0.0
    Returns:
        interpolated_value (float)   : same size as grid['lon']
    """
    print '[info]: Interpolating coastal data onto the grid.' 
    xi = grid['lon']
    yi = grid['lat']
    zi = grid['depth']
    
    [dataLon, dataLat, dataVal] = data   
    # Force ALL grid values deeper than isobathToTaper to 0.0
    # Do not use this method with RBF - will run out of memory    
    ind = np.where( zi > isobathToTaper)
    for n in np.squeeze(ind):
        dataLon.append( xi [n])
        dataLat.append( yi [n])
        dataVal.append( 0.0 )
    
    return griddata((dataLon, dataLat), dataVal, (xi, yi), method='linear')

#==============================================================================
if __name__ == "__main__":  
    
    #Grid
    grid   = adcirc.readGrid ('../adcirc/fort.14')    
    # Data
    data      = readLonLatVal ('xybias.csv')
    
    vi = interpCoastal(grid, copy.deepcopy(data))

    clim  =[-0.15,0.30]    
#    lonlim=[-100, -65] 
#    latlim=[ 20,  45]
    lonlim=[ grid['lon'].min(), grid['lon'].max()]
    latlim=[ grid['lat'].min(), grid['lat'].max()]
    
    # Plot the result    
    import plotter    
    F = plotter.plotSurfaceOnMap(grid, vi, 
                                 clim=clim, lonlim=lonlim, latlim=latlim)
    # Add original data as circles
    import matplotlib.pyplot as plt
    plt.scatter(data[0], data[1], c=data[2], edgecolor='k',cmap=F['cmap'],
                vmin=clim[0], vmax=clim[1], alpha=1.0)
    plt.title('InterpCoastal')
    plt.savefig('interpCoastal.png')
#
