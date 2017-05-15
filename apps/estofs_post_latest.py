# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 2017

@author: Sergey.Vinogradov
"""
import sys, os
sys.path.insert(0,"./csdlpy")
import estofs
import valstat
#import csdldata
from obs import shef
import numpy as np
from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt

#====================================================================
def timeseries_rmsd (obs_dates, obs_values, mod_dates, mod_values, fig=None, title=None):
    """
    Project obs and model onto the same timeline;
    Compute RMSD
    """
    #Sort by date
    obs_dates  =  np.array(obs_dates)
    obs_values =  np.array(obs_values)
    ind = np.argsort(obs_dates)
    obs_dates  = obs_dates[ind]
    obs_values = obs_values[ind]
    # Remove nans
    ind = np.logical_not(np.isnan(obs_values))
    obs_dates   = obs_dates[ind]
    obs_values  = obs_values[ind]
    obs_mean    = np.nanmean (obs_values)
    #Sort by date
    mod_dates  =  np.array(mod_dates)
    mod_values =  np.array(mod_values)
    ind = np.argsort(mod_dates)
    mod_dates  = mod_dates[ind]
    mod_values = mod_values[ind]
    mod_mean   = np.nanmean (mod_values)

    # Remove nans
    ind = np.logical_not(np.isnan(mod_values))
    mod_dates   = mod_dates[ind]
    mod_values  = mod_values[ind]

    refStepMinutes=6
    refDates, obsValProj, modValProj = valstat.projectTimeSeries(obs_dates, obs_values, 
                                                              mod_dates, mod_values, 
                                                              refStepMinutes)
    rmsd = valstat.rms (obsValProj-modValProj) 
    N    = len(obsValProj)

    d = datetime.utcnow()
    if fig:
        plt.figure(figsize=(20,4.5))
        plt.plot(obs_dates, obs_values, '.', color='g',label='OBS')
        plt.plot(mod_dates, mod_values, '.', color='b',label='MOD')
        plt.ylim([-2.0, 3.0])
        plt.plot([d,d], [-2.0, 3.0],'g')
        plt.plot( obs_dates, obs_mean*np.ones(len(obs_dates)),'g-')
    
        plt.plot([mod_dates[0],mod_dates[0]],[-2.0, 3.0],'b')
        plt.plot(mod_dates, mod_mean*np.ones(len(mod_dates)),'b-')   
        if title is None:
            plt.title(fig+' RMSD=' +str(round(rmsd,3)) + ' m')
        else:
            plt.title(title+' RMSD='+str(round(rmsd,3)) + ' m')

        plt.legend(bbox_to_anchor=(0.2, 0.25))
        plt.grid()
        plt.xlabel('DATE UTC')
        plt.ylabel('WL, meters LMSL')
        plt.savefig('ts.'+fig+'.png')
        plt.close()
    return {'rmsd' : rmsd,
            'N'    : N}    

#==============================================================================
if __name__ == "__main__":
    # read data
    obs = shef.read_shef()

    fcst = estofs.latestForecast()
    nowFile = fcst['yyyymmdd']+'.'+fcst['tHHz']  
    ncFile = '/prod/estofs_atl.' + fcst['yyyymmdd'] + '/estofs.atl.' + fcst['tHHz'] + '.points.cwl.nc'
    estofs = estofs.getPointsWaterlevel (ncFile)
    
    counter = 0
    rms = 0.

    for coops_id in obs.keys(): #['COOPS-ID']: #estofs2['stations']:
        nSt = 0
        print str(coops_id)
        nSt = [i for i, s in enumerate(estofs['stations']) if coops_id in s]
        if len(nSt)>0:
            nSt = nSt[0]
            figFile = nowFile+'.'+coops_id

            obs_dates =  obs[coops_id]['dates']
            obs_vals  =  np.squeeze(obs[coops_id]['values'])

            mod_dates =  estofs['time']
            mod_vals  =  np.squeeze(estofs['zeta'][:,nSt])
            stationName = estofs['stations'][nSt]
            print stationName

            stat = timeseries_rmsd (obs_dates, obs_vals, mod_dates, mod_vals, figFile, stationName)

            rmsd = stat['rmsd']
            N    = stat['N']
            counter += 1
            rms = rms + rmsd    
            print 'rmsd=' + str(rmsd)                

        else:        
            print '[warn]: Station does not exist in V2 ' + str(coops_id)
        
    rmsd = rms/float(counter)
        
    print '-------------------------------------------------'
    print '[info]: rmsd=' + str(rmsd)
    
    
    command = 'tar -cvf ' + nowFile + '.tar ts.*.png'
    os.system(command)
    command = 'rm -rf ' + nowFile + 'tar.gz'
    os.system(command)
    command = 'gzip ' + nowFile + '.tar'
    os.system(command)
    command = 'rm -rf ts.*.png'
    os.system(command)


