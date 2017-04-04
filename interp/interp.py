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
    Computes Shepard's invese distance weighted interpolation
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
def decay_linear (z_full, z_zero, zg, vg):
    """
    Tapers the values of the field to zero in between the two specified depths
    Args:
        z_full (float) : depth at which the tapering starts 
        z_zero (float) : depth at which the field fully tapered to zero
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

if __name__ == "__main__":  
    
    from adcirc import readGrid
    from obs.coops import readLonLatVal
    #Grid
    grid   = readGrid ( \
            'C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/adcirc/fort.14')    
    xg = grid['lon']
    yg = grid['lat']
    zg = grid['depth']
    vg = np.zeros(len(xg), dtype=float)
    
    # Data
    data   = readLonLatVal ( \
            'C:/Users/sergey.vinogradov/JET/matlab/bias_work/xybias_liang.csv')
    x = data[0][:]
    y = data[1][:]
    v = data[2][:]
    
    z_full  = 50.
    z_zero  = 200.
    
    p = 2.0
    ind_shelf     = np.where(zg < z_zero)[0]
    vg[ind_shelf] = shepard_idw (x, y, v, xg[ind_shelf], yg[ind_shelf], p=2)
       

    print '[info]: z-decay...'
    ind_decay     = np.where(np.logical_and(z_full <= zg, zg <= z_zero))[0]
    vg[ind_decay] = decay_linear (z_full, z_zero, zg[ind_decay], vg[ind_decay])
    
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
   
    F1 = plotter.plotMap (fig=None, lonlim=lonlim, latlim=latlim)
    F1 = plotter.plotSurface(grid, vg, fig = F1['fig'], 
                                 clim=clim, lonlim=lonlim, latlim=latlim)
    F1 = plotter.plotTriangles (data, threshold=0.0, cmap=F1['cmap'],
                   fig=F1['fig'], clim=clim)
    plt.colorbar()
    plt.title('IDW Shepards p=' + str(p) + 
                  ' with z-decay from '+str(z_full)+ ' to ' + str(z_zero))

