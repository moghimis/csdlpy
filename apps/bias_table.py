# -*- coding: utf-8 -*-
"""
@author: Sergey.Vinogradov
"""
import sys
import datetime as dt
import shutil
sys.path.insert(0,'/u/Sergey.Vinogradov/nos_noscrub/csdlpy')
from obs import shef
    
#==============================================================================
if __name__ == "__main__":
    """
    Script to run daily on devprod machine
    """
    datestr = dt.datetime.strftime(dt.datetime.now(),'%Y%m%d')
    archiveFile = '/gpfs/hps/nos/noscrub/Sergey.Vinogradov/bias_daily_archive/' \
                + datestr + '.csv'
    todayFile   = '/gpfs/hps/nos/save/Sergey.Vinogradov/com/today_bias.csv'

    print '[info]: Creating table: ' + archiveFile
    shef.bias_table(archiveFile) 

    print '[info]: Copying today\'s latest: ' + todayFile
    shutil.copy (archiveFile, todayFile)

