# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 12:59:49 2017

@author: Sergey.Vinogradov
"""
import os
#import obs
#import adcirc
#import sys
#sys.path.insert(0,'/u/Sergey.Vinogradov/nos_noscrub/csdlpy')
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import netCDF4
from datetime import datetime
from datetime import timedelta
import numpy as np

#==============================================================================
def latestForecast (now = datetime.utcnow()):
    """
    Returns strings YYYYMMDD and tHHz, where HH=00,06,12,18 for the forecast
    that should already have been produced on WCOSS at the time 'now'
    Default value for 'now' is current UTC time.
    """

    #now = datetime.utcnow()
    print '[info]: UTC now:', now
    yyyy = str(now.year).zfill(4)
    mm   = str(now.month).zfill(2)
    dd   = str(now.day).zfill(2)

    #production schedule (Based on ESTOFS v2 which is ~15 min later than v1)
    t00z = datetime.strptime(yyyy+mm+dd+' 05:20','%Y%m%d %H:%M')
    t06z = datetime.strptime(yyyy+mm+dd+' 11:20','%Y%m%d %H:%M')
    t12z = datetime.strptime(yyyy+mm+dd+' 17:20','%Y%m%d %H:%M')
    t18z = datetime.strptime(yyyy+mm+dd+' 23:20','%Y%m%d %H:%M')

    fxDate = now
    if now < t00z:
        #take previous days t18z
        fxDate = now-timedelta(days=1)
        tHHz         = 't18z'
    elif t00z <= now and now < t06z:
        tHHz         = 't00z'
    elif t06z <= now and now < t12z:
        tHHz         = 't06z'
    elif t12z <= now and now < t18z:
        tHHz         = 't12z'
    elif t18z <= now:
        tHHz         = 't18z'

    yyyymmdd = str(fxDate.year).zfill(4)+ \
               str(fxDate.month).zfill(2)+ \
               str(fxDate.day).zfill(2)

    return {'yyyymmdd' : yyyymmdd,
            'tHHz'     : tHHz} 

#==============================================================================
def getPointsWaterlevel ( ncFile ):    
    """
    Reads water levels at stations 
    Args: 
        'ncFile' (str): full path to netCDF file        
    Returns:
        dict: 'lon', 'lat', 'time', 'base_date', 'zeta', 'stations'
    """
    
    print '[info]: Reading waterlevels from ' + ncFile               
    if not os.path.exists (ncFile):
        print '[error]: File ' + ncFile + ' does not exist.'
        return
    
    nc = netCDF4.Dataset( ncFile )    
    
    ncTitle = nc.getncattr('title')  # Detect ESTOFS version
    if ncTitle.find('V1.') > 0:
        estofsVersion = 1
        xy_mltplr = 0.01745323168310549  #Magic ESTOFS1 Multiplier...
    elif ncTitle.find('V2.') > 0:
        estofsVersion = 2
        xy_mltplr = 1.00
    print '[info]: ESTOFS Version ' + str(estofsVersion)  +' detected.'
    
    zeta       = nc.variables['zeta'][:]
    missingVal = nc.variables['zeta']._FillValue
    if estofsVersion == 2:
        zeta.unshare_mask()
    zeta [zeta == missingVal] = np.nan
                          
    lon  = xy_mltplr*nc.variables['x'][:]
    lat  = xy_mltplr*nc.variables['y'][:]    
    tim  =           nc.variables['time'][:]    
    
    baseDate = datetime.strptime(nc.variables['time'].base_date[0:19],
                                 '%Y-%m-%d %H:%M:%S')
    realtime = np.array([baseDate + 
                         timedelta(seconds=int(tim[i])) 
                         for i in range(len(tim))])
    
    nam  = nc.variables['station_name'][:][:]
    stations = [''.join([str(x) for x in nam[y]]) for y in range(len(nam))]

    return  {'lat'       : lat, 
             'lon'       : lon, 
             'time'      : realtime, 
             'base_date' : baseDate, 
             'zeta'      : zeta, 
             'stations' : stations}        

#==============================================================================
def getFieldsWaterlevel ():
    print '[error]: not yet implemented'

#==============================================================================
def analyzeForecast ():
    print '[error]: not yet implemented'

#==============================================================================
def validateForecast ():
    print '[error]: not yet implemented'

#==============================================================================
def archiveForecast ():
    print '[error]: not yet implemented'

#==============================================================================
def plotPointWaterLevel ():
    print '[error]: not yet implemented'

#==============================================================================
def plotFieldWaterLevel ():
    print '[error]: not yet implemented'

#==============================================================================
if __name__ == "__main__":    

    ncFile = '/com/estofs/prod/estofs.20170412/estofs.atl.t00z.points.cwl.nc' 
    estofs1 = getPointsWaterlevel (ncFile)

    ncFile = '/gpfs/hps/nco/ops/com/estofs/para/estofs_atl.20170412/estofs.atl.t00z.points.cwl.nc'
    estofs2 = getPointsWaterlevel (ncFile)

#    plt.plot (estofs2['lon'], estofs2['lat'],'bo')
#    plt.plot (estofs1['lon'], estofs1['lat'],'k.')

    coops_id = '8534720'
    plt.figure(figsize=(15,4))
    nSt1 = [i for i, s in enumerate(estofs1['stations']) if coops_id in s][0] #20
    nSt2 = [i for i, s in enumerate(estofs2['stations']) if coops_id in s][0] #22
    plt.plot(estofs1['time'],estofs1['zeta'][:,nSt1],'k')
    plt.plot(estofs2['time'],estofs2['zeta'][:,nSt2],'b')
    plt.title(estofs2['stations'][nSt2])
    plt.legend(['V1','V2'])
    plt.savefig('wl-test.png')
    
