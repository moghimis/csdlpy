# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 10:45:00 2017

@author: Sergey.Vinogradov
"""
import numpy as np

#==============================================================================
def distance_matrix(x0, y0, x1, y1):
    """
    Computes euclidean distance matrix, fast
    from <http://stackoverflow.com/questions/1871536>
    """    
    print '[info]: computing distance matrix...'
    obs    = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

#==============================================================================
def shepard_idw(x, y, v, xi, yi, p=2):
    """
    Computes Shepard's inverse distance weighted interpolation
    Args:
        x, y, v (float) : arrays for data coordinates and values
        xi,  yi (float) : arrays for grid coordinates
        p         (int) : scalar power (default=2)
    Returns:
        vi      (float) : array of v interpolated onto xi and yi
    """       
    dist = distance_matrix(x, y, xi, yi)    

    print '[info]: computing IDW...'
    vi = np.zeros(len(xi), dtype=float)
    weights = 1.0/np.power(dist, p)
    
    #TODO: Optimize!
    for n in range(len(xi)):
        A = 0.
        B = 0.
        for j in range(len(x)):
            A = A + weights[j,n]*v[j]
            B = B + weights[j,n]
        vi[n] = A/B
    return vi

#==============================================================================
def taper_linear (z_full, z_zero, zg, vg):
    """
    Tapers the values of the field to zero in between the two specified depths
    Args:
        z_full (float) : depth at which the tapering starts 
        z_zero (float) : depth at which the field fully tapers to zero
        zg     (float) : array of depths (larger numbers are deeper)
        vg     (float) : array of values to taper        
    Returns:
        vg     (float) : tapered array
    """
    print '[info]: computing linear decay...'
    
    #TODO: Optimize
    for n in range(len(vg)):
        w = (zg[n]-z_zero)/(z_full-z_zero)
        vg[n] = w*vg[n]
    return vg

#==============================================================================
def taper_exp (z_full, z_zero, zg, vg):
    """
    Tapers the values of the field to zero in between the two specified depths
    Args:
        z_full (float) : depth at which the tapering starts 
        z_zero (float) : depth at which the field fully tapers to zero
        zg     (float) : array of depths (larger numbers are deeper)
        vg     (float) : array of values to taper        
    Returns:
        vg     (float) : tapered array
    """
    print '[info]: Computing exponential decay...'
    
    #TODO: Optimize
    for n in range(len(vg)):
        #w = (zg[n]-z_zero)/(z_full-z_zero)
        if zg[n]>z_full:
            w     = z_zero/(z_zero-z_full)*(z_full/zg[n]-1.0) + 1.0
            vg[n] = w*vg[n]
    return vg

#==============================================================================

if __name__ == "__main__":  
    
    from adcirc import readGrid
    from obs.coops import readLonLatVal
    #Grid
    grid   = readGrid ( \
            '../adcirc/fort.14')    
    xg = grid['lon']
    yg = grid['lat']
    zg = grid['depth']
    vg = np.zeros(len(xg), dtype=float)
    
    # Data
    data   = readLonLatVal ( \
            './xybias.csv')
    x = data[0][:]
    y = data[1][:]
    v = data[2][:]
    
    z_full  = 0.   # Depth at which we have full interpolated values
    z_zero  = 200. # Depth at which we have interpolated values tapered to 0. 
    p = 2.0
    
    print '[info]: Interpolate on the shelf...'
    ind_shelf     = np.where(zg < z_zero)[0]
    vg[ind_shelf] = shepard_idw (x, y, v, xg[ind_shelf], yg[ind_shelf], p)

    print '[info]: Taper by depth...'
    ind_taper     = np.where (np.logical_and(z_full <= zg, zg <= z_zero))[0]
    vg[ind_taper] = taper_linear (z_full, z_zero, zg[ind_taper], vg[ind_taper])
    #vg[ind_taper] = taper_exp (z_full, z_zero, zg[ind_taper], vg[ind_taper])
    
    print'[info]: zero out the results that are too distant from data'
    R = 1.5
    dist = distance_matrix(x, y, xg, yg)
    for n in range(len(xg)):
        if np.min(dist[:,n]) > R:
            vg[n] = 0.
    
    clim  =[-0.15,0.30]    
    lonlim=[-87, -78] 
    latlim=[ 23,  33]
    lonlim=[np.min(xg), np.max(xg)]
    latlim=[np.min(yg), np.max(yg)]
    
#    
    print '[info]: Plotting...'
    # Plot the result    
    import matplotlib.pyplot as plt
    import plotter    
   
    F = plotter.plotMap (fig=None, lonlim=lonlim, latlim=latlim)
    F = plotter.plotSurface(grid, vg, fig = F['fig'], 
                                 clim=clim, lonlim=lonlim, latlim=latlim)
    F = plotter.plotTriangles (data, threshold=0.0, cmap=F['cmap'],
                   fig=F['fig'], clim=clim)
    plt.colorbar()
    plt.title('IDW Shepards p=' + str(p) + 
                  ' with z-decay from '+str(z_full)+ ' to ' + str(z_zero) + ', R=' + str(R))

