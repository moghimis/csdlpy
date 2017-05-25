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

import os
import string
import cartopy
from cartopy.feature import NaturalEarthFeature, LAND, COASTLINE
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.io.img_tiles import StamenTerrain

#==============================================================================
def plotTimeSeries ():
    print '[error]: not yet implemented'

#==============================================================================
def plotScatter ():
    print '[error]: not yet implemented'

#==============================================================================
def plotMapC (fig=None, lonlim=[-98.0, -53.8], latlim=[5.8, 46.0],
                      mapResolution='c', figsize=[9,9],
                      layer='BlueMarble_ShadedRelief'):
    """
    Plots a geographic map using Cartopy package
    Args:
    Optional:
        fig (plt.figure)       : figure handle
        lonlim([float, float]) : longitude limits, ([min, max] = default)
        latlim([float, float]) : latitude  limits, ([min, max] = default)
        
        
        layer could be one of:
           None: use default image (low res)
           'BM':   for local Blue marble
           one of these for downloading from NASA web page:
             ['BlueMarble_NextGeneration', 'VIIRS_CityLights_2012',
             'Reference_Features', 'Sea_Surface_Temp_Blended', 'MODIS_Terra_Aerosol',
             'Coastlines', 'BlueMarble_ShadedRelief', 'BlueMarble_ShadedRelief_Bathymetry']
    
    
    Returns:
        m (Basemap handle) 
        fig (plt.figure handle)
    """
    
    print '[info]: Plotting the Map.'    
    dx = lonlim[1]-lonlim[0]
    
    #Set resolution depending on longitudinal swath
    dparallels, dmeridians = 10., 10.    
    if mapResolution == 'c':
        if dx <= 50.0:
            mapResolution = '50m'  #'110m'
            dparallels = dmeridians = 5.0
        if dx <= 15.0:
            mapResolution = '50m'
            dparallels = dmeridians = 2.0
        if dx <=  5.0:
            mapResolution = '10m'
            dparallels = dmeridians = 1.0
        print '[info]: Resolution is set to ' + mapResolution
               
    if fig is None:
        fig = plt.figure(figsize=figsize)    

    ax = fig.add_axes([0.1,0.1,0.85,0.85],projection=cartopy.crs.PlateCarree())
    extents = np.array([lonlim,latlim]).flatten()
    ax.set_extent(extents)
    ax.coastlines(mapResolution)

    layers = ['BlueMarble_NextGeneration', 'VIIRS_CityLights_2012',
             'Reference_Features', 'Sea_Surface_Temp_Blended', 'MODIS_Terra_Aerosol',
             'Coastlines', 'BlueMarble_ShadedRelief', 'BlueMarble_ShadedRelief_Bathymetry']
    if layer == 'BM':
        print '[info]: Use BlueMarble: Cartopy 0.15 or newer is needed' 
        #generate path to csdlpy location
        path =  os.path.abspath(adcirc.__file__).split('/')[:-2]
        path = string.join(path,'/')
        os.environ["CARTOPY_USER_BACKGROUNDS"] = os.path.join(path,'BG/')
        ax.background_img(name='BM', resolution='high')
    elif layer in layers :
        print '[info]: Downloading from NASA: layer = ', layer
        url = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
        ax.add_wmts(url, layer_name=layer)
    else:
        ax.stock_img()
 
    ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    ax.add_feature(cartopy.feature.RIVERS)
        
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return {'map' : ax, 'fig' : fig}

#==============================================================================
def plotMap (fig=None, lonlim=[-98.0, -53.8], latlim=[5.8, 46.0],
                      mapResolution='c', figsize=[9,9]):
    """
    Plots a geographic map using Basemap package
    Args:
    Optional:
        fig (plt.figure)       : figure handle
        lonlim([float, float]) : longitude limits, ([min, max] = default)
        latlim([float, float]) : latitude  limits, ([min, max] = default)
    Returns:
        m (Basemap handle) 
        fig (plt.figure handle)
    """
    
    print '[info]: Plotting the Map.'    
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
        fig = plt.figure(figsize=figsize)    
        
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
    plt.xlabel('LONGITUDE')
    plt.ylabel('LATITUDE')        
    return {'map' : m, 'fig' : fig}

#==============================================================================
def plotPoints (data, 
                fig=None, ssize = 20, cmap=None,
                clim=[-0.5, 0.5]):
    """
    Plots sparse data as circles
    """
    print '[info]: Plotting the points.'
    x = data[0]
    y = data[1]
    v = data[2]    

    if fig is None:
        fig = plt.figure(figsize=(9,9))    
    
    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (x, y, c=v, marker='o', s=ssize, edgecolors='k', cmap = cmap)
    plt.clim(vmin=clim[0], vmax=clim[1])
    
    return {'fig' : fig, 'cmap' : cmap}

#==============================================================================
def plotTriangles (data, threshold=0.0,
                   fig=None,  
                   clim=[-0.5, 0.5], cmap=None):
    """
    Plots sparse data as triangles, uward- or downward-looking depending
    if the value exceeds a threshold or not.
    """
    print '[info]: Plotting the triangles.'
    x = data[0]
    y = data[1]
    v = data[2]    
    
    # Block below can be somehow optimized, right?
    ind_up = [i for i, e in enumerate (v) if e >= threshold]
    ind_dn = [i for i, e in enumerate (v) if e <  threshold]   
    xup  = [x[i] for i in ind_up]
    yup  = [y[i] for i in ind_up]
    vup  = [v[i] for i in ind_up]   
    xdn  = [x[i] for i in ind_dn]
    ydn  = [y[i] for i in ind_dn]
    vdn  = [v[i] for i in ind_dn]

    if fig is None:
        fig = plt.figure(figsize=(9,9))    
    if cmap is None:
        cmap = plt.cm.jet        
    plt.scatter (xup, yup, c=vup, marker='^', edgecolors='k', 
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1)
    plt.scatter (xdn, ydn, c=vdn, marker='v', edgecolors='k', 
                 cmap = cmap, vmin=clim[0], vmax=clim[1], alpha=1)        
    
    return {'fig' : fig, 'cmap' : cmap}
    
#==============================================================================
def plotSurface (grid, surface, 
                 clim=[0.0, 3.0], lonlim=None, latlim=None, fig=None):
    """
    Plots a field specified on an unstructured grid
    Args:
        grid    (dict)   : grid     as read by adcirc.readGrid ()
        surface (array or masked_array) : 
                   2d field as read by adcirc.readSurfaceField ()
    Optional:
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
    
    print '[info]: Plotting the surface.'
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
    
    if fig is None:
        fig = plt.figure(figsize=(9,9))    

    myCmap = plt.cm.jet

    fig     = plt.tripcolor(Tri, z, shading='flat',\
                         edgecolors='none', \
                         cmap=myCmap, vmin=clim[0], vmax=clim[1])
    plt.axis([lonlim[0], lonlim[1], latlim[0], latlim[1]])    
    
    return {'fig' : fig, 'cmap' : myCmap}

#==============================================================================
if __name__ == "__main__":

    grid   = adcirc.readGrid ('../adcirc/fort.14')    
    maxele = adcirc.readSurfaceField ('maxele.nc', 'zeta_max' ) 
   
    # Demo masked array:    
    lonlim=[-74.5,-71.5]
    latlim=[ 39.9, 41.6]
    clim = [  -0.5, 0.5]
    
    #using Basemap
    cf2 = plotMap     ( lonlim=lonlim, latlim=latlim)
    cf2 = plotSurface (grid, maxele['value'], fig = cf2['fig'],
                       clim=clim,
                       lonlim=lonlim, latlim=latlim)

    #using Cartopy for BlueMarble background
    cf2 = plotMapC    ( lonlim=lonlim, latlim=latlim, layer='BM')
    cf2 = plotSurface (grid, maxele['value'], fig = cf2['fig'],
                       clim=clim,
                       lonlim=lonlim, latlim=latlim)    

    
# Data
    from obs.coops import readLonLatVal

    data   = readLonLatVal ('../interp/xybias.csv')
    cf2 = plotTriangles (data, threshold=0.0,
                   fig=cf2['fig'],  
                   clim=[-0.5, 0.5], lonlim=lonlim, latlim=latlim)
    plt.colorbar()
    
