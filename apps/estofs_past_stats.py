# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 2017

@author: Sergey.Vinogradov
"""
import sys, os
sys.path.insert(0,"/gpfs/hps/nos/noscrub/Sergey.Vinogradov/csdlpy")
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
def timeseries_rmsd (obs_dates, obs_values, mod_dates, mod_values, fig=None):
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
    
    #Sort by date
    mod_dates  =  np.array(mod_dates)
    mod_values =  np.array(mod_values)
    ind = np.argsort(mod_dates)
    mod_dates  = mod_dates[ind]
    mod_values = mod_values[ind]
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

    if fig:
        plt.figure(figsize=(20,4.5))
        plt.plot(obs_dates, obs_values, '.', color='g',label='OBS')
        plt.plot(mod_dates, mod_values, '.', color='b',label='MOD')
        plt.ylim([-3.0, 3.0])
        plt.title(fig+', RMSD=' +str(rmsd))
        plt.legend(bbox_to_anchor=(0.9, 0.35))
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

    val = '2017041600'
    startDate = datetime.strptime(val,'%Y%m%d%H')
    endDate   = datetime.utcnow()
    dates = np.arange(startDate, endDate, timedelta(hours=6)).astype(datetime)
    
    stats_dates = []
    stats_rmsd1 = []
    stats_rmsd2 = []
    stats_cnt1  = []
    stats_cnt2  = []

    f = open('rmsd-' + val + '.txt','w+',0)
    
    for d in dates:
        
        fcst = estofs.latestForecast(d)
        #f.write(str(d) + ', ' + fcst['yyyymmdd'] + '.' + fcst['tHHz'] + '\n')
        # ESTOFS v1
        ncFile  = '/com/estofs/prod/estofs.' + fcst['yyyymmdd'] + '/estofs.atl.' + fcst['tHHz'] + '.points.cwl.nc'
        estofs1 = estofs.getPointsWaterlevel (ncFile)

        # ESTOFS v2
        ncFile = '/gpfs/hps/nco/ops/com/estofs/para/estofs_atl.' + fcst['yyyymmdd'] + '/estofs.atl.' + fcst['tHHz'] + '.points.cwl.nc'
        estofs2 = estofs.getPointsWaterlevel (ncFile)

        counter1 = 0
        counter2 = 0
        rms1 = 0.
        rms2 = 0.

        for coops_id in obs.keys(): #['COOPS-ID']: #estofs2['stations']:
            nSt1 = 0
            print str(coops_id)
            nSt1 = [i for i, s in enumerate(estofs1['stations']) if coops_id in s][0]
                if len(nSt1)>0:
                    stat1 = timeseries_rmsd (obs[coops_id]['dates'], obs[coops_id]['values'], 
                                             estofs1['time'], estofs1['zeta'][:,nSt1],
                                             fcst['yyyymmdd'] + '.' + fcst['tHHz'] + '.' + coops_id + '.v1')
                    rmsd1 = stat1['rmsd']
                    N1    = stat1['N']
                    counter1 += 1
                    rms1 = rms1 + rmsd1    
                    print 'rmsd1=' + str(rmsd1)                

                    nSt2 = [i for i, s in enumerate(estofs2['stations']) if coops_id in s][0]
                    if len(nSt2)>0:
                        t = estofs2['zeta'][:,nSt2].unshare_mask()
                        t[t==estofs2['zeta'].fill_value] = np.nan
                        stat2 = timeseries_rmsd (obs[coops_id]['dates'], obs[coops_id]['values'], 
                                                 estofs2['time'] + timedelta(seconds=30), t,
                                                 fcst['yyyymmdd'] + '.' + fcst['tHHz'] + '.' + coops_id + '.v2')
                        rmsd2 = stat2['rmsd']
                        N2    = stat2['N']
                        counter2 += 1
                        rms2 = rms2 + rmsd2
                        print 'rmsd2=' + str(rmsd2)                    
                        printString = coops_id+','+str(d)+','+"".join(str(rmsd1))+','+str(N1)+','+"".join(str(rmsd2))+','+str(N2)+'\n'
                        print printString
                        f.write( printString )
                        if rmsd2 > 1.0:
                            print str(estofs2['zeta'][:,nSts2])
                            sys.exit()

                    f.flush()
                    os.fsync(f.fileno()) 
            else:        
                print '[warn]: Station does not exist in V1 ' + str(coops_id)
        
        rmsd1 = rms1/float(counter1)
        rmsd2 = rms2/float(counter2)
        stats_rmsd1.append(rmsd1)
        stats_rmsd2.append(rmsd2)
        stats_cnt1.append(counter1)
        stats_cnt2.append(counter2)
        stats_dates.append(d)
        
        print '-------------------------------------------------'
        print '[info]: date= ' + str(d) + ' rmsd1=' + str(rmsd1) + ', rmsd2=' + str(rmsd2)

        f.write(str(d) + ' MEAN RMSD V1=' + 
            ',' + str(rmsd1) + ', stations=' + str(counter1) + 
            ', MEAN RMSD V2=' + str(rmsd2) + ', stations=' + str(counter2) + '\n')
    f.close()
    

