# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:06:00 2017

@author: Sergey.Vinogradov
"""
import sys
import urllib
import numpy as np
from datetime import datetime
from datetime import timedelta as dt

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
        
        'units' (str): 'meters','feet'.
        
    Returns:
        data (dict): retrieved time series record of observations.
    
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
    
    
    # Formulate, print and send the request
    serverSide = 'http://opendap.co-ops.nos.noaa.gov/axis/webservices/'
    # Parse the response
    
    data = None
    return data


if __name__ == "__main__":
    
    now   = datetime.now()
    lweek = (now-dt(days=7), now)
    cwlev = getdata('8518750', lweek)        
    tides = getdata('8518750', lweek, product='predictions')        
    print tides    


#https://opendap.co-ops.nos.noaa.gov/axis/webservices/waterlevelrawsixmin/plain/response.jsp?stationId=8454000&beginDate=20170315&endDate=20170315&datum=MLLW&unit=0&timeZone=0&Submit=Submit
