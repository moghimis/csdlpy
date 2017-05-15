# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:07:49 2017

@author: Sergey.Vinogradov
"""
import numpy as np
from datetime import datetime
from datetime import timedelta


#============================================================================== 
def nearest(items, pivot):
    """
    Finds an item in 'items' list that is nearest in value to 'pivot'
    """
    nearestVal = min(items, key=lambda x: abs(x - pivot))
    try:
        items = items.tolist()
    except:
        pass
    indx = items.index(nearestVal)
    return nearestVal, indx

#==============================================================================
def rms(V):
    """
    Returns Root Mean Squared of the time series V (np.array)
    """    
    ind = np.logical_not(np.isnan(V))
    V = V[ind]
    summ = np.sum(V**2)
    N = 1.0*len(V)
    return np.sqrt( summ/N )

#============================================================================== 
def projectTimeSeries (obsDates, obsVals, modDates, modVals, refStepMinutes=6):
    """
    Projects two timeseries (obsDates, obsVals) and (modDates, modVals)
    onto a common reference time scale with a resolution defined by
    refStepMinutes. 
    Note: tolerance for dates projection is half of refStepMinutes.
    Args:
        obsDates (datetime np.array of length Lobs ) : dates  for timeseries 1
        obsVals  (np.array of length Lobs)           : values for timeseries 1
        modDates (datetime np.array of length Lmod ) : dates  for timeseries 2
        modVals  (np.array of length Lmod)           : values for timeseries 2
        refStepMinutes (int, default=6)              : projection time step.
    Returns:
        refDates    (datetime np.array)  : projection dates
        obsValsProj (np.array)           : projected values of timeseries 1
        modValsProj (np.array)           : projected values of timeseries 2
    """
    # Create reference time line
    refStart = np.maximum(np.min(obsDates), np.min(modDates))
    refEnd   = np.minimum(np.max(obsDates), np.max(modDates))
    refStep  = timedelta(minutes=refStepMinutes)
    prec     = timedelta(minutes=0.5*refStepMinutes)
    
    refDates = np.arange(refStart, refEnd, refStep).astype(datetime)

    # Project obs and model onto reference time line
    obsValsProj  = []    
    modValsProj  = []

    for t in refDates:
        #find t in obsDates within refStep
        nearestObsDate, idx = nearest(obsDates, t)
        if abs(nearestObsDate - t) < prec:
            nearestObsVal   = obsVals[idx]
            obsValsProj.append (nearestObsVal)
        else:
            obsValsProj.append (np.nan)
            
        nearestModDate, idx = nearest(modDates, t)
        if abs(nearestModDate - t) < prec:
            nearestModVal   = modVals[idx]
            modValsProj.append (nearestModVal)
        else:
            modValsProj.append (np.nan)
    return refDates, np.array(obsValsProj), np.array(modValsProj)

#==============================================================================
if __name__ == "__main__":
    # Create discontinuous obs time series
    from datetime import datetime
    from datetime import timedelta
    import matplotlib.pyplot as plt
    matplotlib.use('Agg',warn=False)    
    
    obsStep  = timedelta(minutes=6)
    obsStart1 = datetime(2017,04,19,6,6,0)
    obsEnd1   = datetime(2017,04,19,8,6,0)
    obsDates1 = np.arange(obsStart1, obsEnd1, obsStep).astype(datetime)
    obsStart2 = datetime(2017,04,19,8,24,0)
    obsEnd2   = datetime(2017,04,19,10,6,0)
    obsDates2 = np.arange(obsStart2, obsEnd2, obsStep).astype(datetime)
    obsDates = np.concatenate((obsDates1, obsDates2),axis=0)
    # Impose some NaNs in obs time series
    obsVals  = np.zeros(len(obsDates))
    for i in range(len(obsVals)):
        obsVals[i] = np.cos(i)
        obsVals[34] = np.nan
   
    # Create model time series
    modStart = datetime(2017,04,19,6,11,30)
    modEnd   = datetime(2017,04,19,10,6,30)
    modStep  = timedelta(minutes=8)
    modDates = np.arange(modStart, modEnd, modStep).astype(datetime)
    modVals  = np.zeros(len(modDates))
    for i in range(len(modVals)):
        modVals[i] = np.sin(i)
    # Impose NaNs in model values
    modVals[12] = np.nan       
    
    plt.plot(obsDates, obsVals,'.-g')
    plt.plot(modDates, modVals,'.-b')

    refStepMinutes = 6
    refDates, obsValsProj, modValsProj = projectTimeSeries (obsDates,
                                                            obsVals,
                                                            modDates,
                                                            modVals,
                                                            refStepMinutes)
    plt.plot(refDates, obsValsProj,'--go',markerfacecolor='none')
    plt.plot(refDates, modValsProj,'--bo',markerfacecolor='none')
    print rmse(obsValsProj, modValsProj)    
    
