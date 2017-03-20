# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:06:00 2017

@author: Sergey.Vinogradov
"""
import os, sys
import wget
import numpy as np
from datetime import datetime
from datetime import timedelta as dt

#==============================================================================
def getdata (stationID,  dateRange, 
             product='waterlevelrawsixmin', datum='MSL', units='meters'):
    
    """ 
    Allows for downloading the observations from NOAA's 
    Center for Operational Oceanographic Products and Services (COOPS)
    via OpenDAP server    http://opendap.co-ops.nos.noaa.gov .
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID.
        dateRange (datetime, datetime): start and end dates of retrieval.
    
    Optional Args:        
        'product' (str):             
            WATER LEVEL: 
            'waterlevelrawsixmin' (=default), 'waterlevelrawonemin',
            'waterlevelverifiedsixmin',  'waterlevelverifiedhourly',
            'waterlevelverifiedhighlow', 'waterlevelverifieddaily', 
            'waterlevelverifiedmonthly',
            'highlowtidepredictions', 'predictions', 
            'harmonicconstituents',    'datums',             
            METEOROLOGY: 
            'barometricpressure', 'wind'. 
            
        'datum' (str): 'MSL' (=default), 'NAVD', 'IGLD', 'MTL',
            'station datum', 'MHW','MHHW','MLLW', 'MLW'.
        
        'units' (str): 'meters','feet', 'm/sec', 'knots','miles/hour'
        
        'tideFreq' (str): '6' (=default), '60'
        
    Returns:
        ('dates' (datetime), 'values' (float)): 
            retrieved time series record of observations.
            Note: for the 'wind' product, 'values' consist of 
            wind speed, wind direction and wind gust.
            
    Examples:
        now   = datetime.now()
        dates = (now-dt(days=3), now)
        tides = getdata('8518750', dates, product='predictions')        
        retrieves tidal water levels at The Battery, NY over the last 3 days.
        
    """
    # Check dateRange
    # 'waterlevel*'       : months=12
    # 'waterlevelverifiedhighlow' : months=5*12
    # 'waterlevel*sixmin' : months=1
    # ''
    # If needed call sub-function to split dateRange into proper chunks
    # and call getdata recursively and concatenate the outputs
    
    ## Formulate, print and send the request
    serverSide  = 'http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
    timeZoneID  = '0'

    unitID      = '1'  # feet, or knots
    if units   == 'meters' or units == 'm/sec':
        unitID  = '0'    
    elif units == 'miles/hour':
        unitID  = '2'

    tideFreq    = '6'  # use 60 for hourly tides
    tideFreqStr = ''
    if product == 'predictions':
        tideFreqStr = '&dataInterval=' + tideFreq
        
    request = ( serverSide + product + '/plain/response.jsp?stationId=' + 
               stationID + 
               '&beginDate=' + dateRange[0].strftime("%Y%m%d") +
               '&endDate='   + dateRange[1].strftime("%Y%m%d") +
               '&datum=' + datum + '&unit=' + unitID + 
               '&timeZone=' + timeZoneID + tideFreqStr + 
               '&Submit=Submit')
    print '[info]: Downloading ', request
    
    tmpFile  = wget.download (request)
    lines    = open(tmpFile).readlines()
    os.remove (tmpFile)
        
    ## Parse the response
    dates  = []
    values = []   
    for line in lines:
        if ('waterlevel' in product):
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[31:38]))
            except:
                pass
        elif product == 'predictions':
            try:
                dates.append  (datetime.strptime(line[ 9:25],'%m/%d/%Y %H:%M'))
                values.append (float(line[26:]))
            except: 
                pass
        elif product == 'barometricpressure':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[30:37]))
            except: 
                pass
        elif product == 'wind':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append ([float(line[30:37]),
                                float(line[38:45]),
                                float(line[46:53])])
            except: 
                pass
        else:
            print '[error]: product [' + product + '] is not yet implemented!'
            break
        
    return {'dates' : dates, 'values' : values}       


#==============================================================================
def getStationInfo (stationID):
    
    """
    Downloads geographical information for a CO-OPS station
    from http://tidesandcurrents.noaa.gov
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID
    
    Returns:
        'info' (dict): ['name']['state']['lon']['lat']

    Examples:
        & getStationInfo('8518750')['name']
        & 'The Battery'
    """
    request = ( 'https://tidesandcurrents.noaa.gov/stationhome.html?id=' +
               stationID )
    tmpFile  = wget.download   (request)
    lines    = open(tmpFile).readlines()
    os.remove (tmpFile)
    
    try:
        for line in lines:
            if 'var station_name'  in line:
                stationName  = line.split('"')[1]
            if 'var station_state' in line:
                stationState = line.split('"')[1]
            if 'var lat'           in line:
                lat          = float(line.split('"')[1])
            if 'var lon'           in line:
                lon          = float(line.split('"')[1])           
        
        return {'name' : stationName, 'state' : stationState,
                'lon'  : lon, 'lat' : lat }
    except:
        print '[error]: cannot get info for  ' + stationID
        return None

#==============================================================================
if __name__ == "__main__":

    ## Demo the methods by downloading and plotting products at a station
    stationID = '8454000'
    info  = getStationInfo (stationID)
    now   = datetime.now()
    lday  = (now-dt(days=1), now)
    cwlev = getdata(stationID , lday)        
    tides = getdata(stationID , lday, product='predictions')        
    press = getdata(stationID , lday, product='barometricpressure')
    wind  = getdata(stationID , lday, product='wind')
    windSpeed = []
    for w in wind['values']:
        windSpeed.append(w[0])
    
    import matplotlib
    import matplotlib.pyplot as plt
    f1 = plt.figure(figsize=(9,4))
    plt.plot(tides['dates'], tides['values'], label='tides',color='b')
    plt.plot(cwlev['dates'], cwlev['values'], label='cwlev',color='g')
    plt.title('Water Levels at ' + info['name'])
    plt.legend()
    ax1 = f1.gca()
    ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
 
