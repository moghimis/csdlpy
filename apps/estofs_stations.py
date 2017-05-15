# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 16:43:32 2017

@author: Sergey.Vinogradov
"""
import sys
sys.path.insert(0,"/u/Sergey.Vinogradov/git/pySHEF")
sys.path.insert(0,"/gpfs/hps/nos/noscrub/Sergey.Vinogradov/csdlpy")
import estofs
#import csdldata
from obs import shef
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import numpy as np

#==============================================================================
if __name__ == "__main__":
    # read data
    obs = shef.read_shef()
    
    ncFile = '/com/estofs/prod/estofs.20170413/estofs.atl.t00z.points.cwl.nc'
    estofs1 = estofs.getPointsWaterlevel (ncFile)

    ncFile = '/gpfs/hps/nco/ops/com/estofs/para/estofs_atl.20170413/estofs.atl.t00z.points.cwl.nc'
    estofs2 = estofs.getPointsWaterlevel (ncFile)

    #coops_id = '8534720'
    for coops_id in obs.keys(): #['COOPS-ID']: #estofs2['stations']:
        nSt1 = 0
        nSt2 = 0
        print '[info]: Plotting Station ' + coops_id
        try:
            nSt1 = [i for i, s in enumerate(estofs1['stations']) if coops_id in s][0]
        except:
            print '[warn]: Station does not exist in V1'
        try:
            nSt2 = [i for i, s in enumerate(estofs2['stations']) if coops_id in s][0]
        except:
            print '[warn]: Station does not exist in V2'
        plt.figure(figsize=(18,4.5))
        plt.plot(obs[coops_id]['dates'],obs[coops_id]['values'],'.g',label='OBS')
        if nSt1:
            plt.plot(estofs1['time'],estofs1['zeta'][:,nSt1],color='k',label='V1',linewidth=2)
        if nSt2:
            plt.plot(estofs2['time'],estofs2['zeta'][:,nSt2],color='b',label='V2',linewidth=2)
        plt.plot(obs[coops_id]['dates'],obs[coops_id]['values'],'.g')
        plt.ylim([-3.0, 3.0])
        plt.title(estofs2['stations'][nSt2])
        plt.legend(bbox_to_anchor=(0.90, 0.35))
        plt.grid()
        plt.xlabel('DATE UTC')
        plt.ylabel('WL, meters MSL')
        if nSt2:
            print '[info]: Saving figure for station ' + coops_id
            plt.savefig('ts-' + coops_id + '.png')
        plt.close()

