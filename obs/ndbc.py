# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 08:50:00 2017

@author: Sergey.Vinogradov
"""
import os, sys
import wget
import numpy as np
from datetime import datetime
from datetime import timedelta as dt

#==============================================================================
def getdata (stationID,  dateRange, 
             product='WVHT', units='meters'):
    
    """ 
    Allows for downloading the observations from NOAA's 
    National Data Buoy Center (NDBC)
    via ??? server    http://www.ndbc.noaa.gov .
    
    Args:
        stationID (str):              5 character-long NDBC station ID.
        dateRange (datetime, datetime): start and end dates of retrieval.
    
    Optional Args:        
        'product' (str): 'WVHT' (=default), 'DPD', 'APD', MWD', 'WTMP'           
       
        'units' (str): 'meters'  (=default), 'feet', 
                       'celcius' (=default), 'fahrenheit'
        
    Returns:
        ('dates' (datetime), 'values' (float)): 
            retrieved time series record of observations.
            
    Examples:
        now   = datetime.now()
        dates = (now-dt(days=3), now)
        sigWaveHeight = getdata('44091', dates)
        retrieves significant wave height at Barnegat, NJ over the last 3 days.
        
    """
    ## Check dateRanges for server limits, slit if necessary
    
    ## Formulate, print and send the request
        
    ## Parse the response
    
    print '[error]: not yet implemented.'
    return None #{'dates' : dates, 'values' : values}       


#==============================================================================
def getStationInfo (stationID):
    
    """
    Downloads geographical information for a NDBC station
    from http://tidesandcurrents.noaa.gov
    
    Args:
        stationID (str):              5 character-long CO-OPS station ID
    
    Returns:
        'info' (dict): ['name']['state']['lon']['lat']

    Examples:
        & getStationInfo('44091')['name']
        & 'Barnegat'
    """
    print '[error]: not yet implemented'
    return None

#==============================================================================
if __name__ == "__main__":

    ## Demo the methods by downloading and plotting products at a station
    stationID = '44091'
    info  = getStationInfo (stationID)
    now   = datetime.now()
    lday  = (now-dt(days=1), now)
    swht  = getdata(stationID , lday)        
    wdir  = getdata(stationID , lday, product='MWD')
    