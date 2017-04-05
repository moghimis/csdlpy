# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 11:29:21 2017

@author: Sergey.Vinogradov
"""
import os
from datetime import datetime as dt
import csv
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import numpy as np
import adcirc
import plotter
import interp

#==============================================================================
def read_bias_file (csvFile):
    """
    Reads bias file in CSV format
    Header is: 
        COOPS-ID, SHEF-ID, lon, lat, 
        Bias MLLW (m), Bias MSL (m), Bias NAVD88 (feet),
        Stat significance (0-1), Length of record (days)
    """
    xo = []
    yo = []
    vo = []    
    
    f = open( csvFile, 'r')
    reader = csv.reader(f)        
    
    next(reader, None)    
    for row in reader:
        xo.append( float(row[2]) )
        yo.append( float(row[3]) )
        vo.append( float(row[5]) )
    return [xo, yo, vo]       
    
#==============================================================================
if __name__ == "__main__":
    """
    Script to run daily on devprod machine, after the latest bias list
    is available.
    Script reads the latest biases, plots them up on the map, 
    saves the map, interpolates biases onto the grid, plots the result
    and saves the file for ADCIRC pseudo
    """
    #0. Configure paths
    ## WCOSS: 
    # csv_path = "/gpfs/hps/nos/save/Sergey.Vinogradov/bias_daily/"
    # pix_path = "/gpfs/hps/nos/save/Sergey.Vinogradov/bias_daily/pix/"
    # grd_file = "/gpfs/hps/nos/save/Sergey.Vinogradov/hsofs/fort.14"
    # ofstFile = "/gpfs/hps/nos/save/Sergey.Vinogradov/bias_daily/pix/offset.63"
    ## Local test
    csv_path = "C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/apps/"
    pix_path = "C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/apps/pix/"
    grd_file = "C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/adcirc/fort.14"
    ofstFile = "C:/Users/sergey.vinogradov/Documents/GitHub/csdlpy/apps/offset.63"
    
    # Configure parameters    
    z_full  = 0.   # Depth at which we have full interpolated values
    z_zero  = 200. # Depth at which we have interpolated values tapered to 0. 
    p = 2.0        # IDW power
    R = 2.0        # Rejection radius
    clim = [-0.5, 0.5] # Color range, in meters
    
    #1. Find out current date
    now = dt.now()
    yyyy = str(now.year).zfill(4)
    mm   = str(now.month).zfill(2)
    dd   = str(now.day).zfill(2)    
    print '[time]: ', now     
    #2. Read latest bias
    csvFile = csv_path + yyyy+mm+dd+'.csv'   
    if os.path.exists(csvFile):
        data = read_bias_file (csvFile)
    else:
        print '[error]: No bias file found! ' + csvFile
        raise Exception('No bias file found!')
    
    #3. Plot as triangles
    x = data[0]
    y = data[1]
    v = data[2]
    rangex = [np.min(x), np.max(x)]
    rangey = [np.min(y), np.max(y)]
    rangev = [np.min(v), np.max(v)]
    vstats = str(round(np.min(v), 2)) + '/' + \
             str(round(np.mean(v),2)) + '/' + \
             str(round(np.max(v), 2))    
    f = plotter.plotMap (
            lonlim=[rangex[0]-1.0, rangex[1]+1.0], 
            latlim=[rangey[0]-1.0, rangey[1]+1.0] , figsize=[15,8] )    
    f = plotter.plotTriangles (data, threshold=0.0, 
                               fig = f['fig'], clim=clim)
    cbar = plt.colorbar()
    cbar.set_label('METERS MSL')
    plt.title(yyyy+mm+dd + ' time-mean biases. min/avg/max=' + vstats  +' m MSL')
    plt.savefig (pix_path + yyyy+mm+dd+ '_biases.png')
    plt.close(f['fig'])
    
    #3. Read the grid
    grid = adcirc.readGrid ( grd_file )
    xg = grid['lon']  [:]
    yg = grid['lat']  [:]
    zg = grid['depth'][:]
    vg = np.zeros(len(xg), dtype=float)
    
    #3.5. Reject data not within grid coverage
    ind_xout = np.where (np.logical_or(x<np.min(xg),x>np.max(xg))) [0]
    for i in ind_xout:
        v[i] = 0.0
    ind_yout = np.where (np.logical_or(y<np.min(yg),y>np.max(yg))) [0]
    for i in ind_yout:
        v[i] = 0.0
     
    #4. Perform interpolation    
    print '[info]: Interpolate on the shelf...'
    ind_shelf     = np.where(zg < z_zero)[0]
    vg[ind_shelf] = interp.shepard_idw (x, y, v, 
                                        xg[ind_shelf], yg[ind_shelf], p)

    print '[info]: Taper by depth...'
    ind_taper     = np.where (np.logical_and(z_full <= zg, zg <= z_zero))[0]
    vg[ind_taper] = interp.taper_linear (z_full, z_zero, 
                                         zg[ind_taper], vg[ind_taper])

    print '[info]: Reject the results that are too distant from data'
    dist = interp.distance_matrix(x, y, xg, yg)
    for n in range(len(xg)):
        if np.min(dist[:,n]) > R:
            vg[n] = 0.
    
    #5. Plot
    print '[info]: Plotting...'
    F = plotter.plotMap (
            lonlim=[np.min(xg)-1.0, np.max(xg)+1.0], 
            latlim=[np.min(yg)-1.0, np.max(yg)+1.0] , figsize=[15,8] )    
    F = plotter.plotSurface(grid, vg,    fig = F['fig'], clim=clim )
    F = plotter.plotTriangles (data, threshold=0.0, cmap=F['cmap'],
                   fig=F['fig'], clim=clim)
    Cbar = plt.colorbar()
    Cbar.set_label('METERS MSL')
    plt.title(yyyy+mm+dd + ' interpolated biases, m MSL')
    plt.savefig (pix_path + yyyy+mm+dd+ '_surface.png')
    plt.close('all')
    print '[time]: ', dt.now()
    print '[info]: elapsed time:', (dt.now()-now).seconds, 'sec'
    
    #6. Save the surface
    adcirc.writeOffset63 (vg, ofstFile)
    