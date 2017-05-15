# -*- coding: utf-8 -*-
"""
This script reads available SHEF data from WCOSS and calculates the water level
anomaly (WLA) from the available stations in the SHEF file. The script outputs 
an ASCII file containing the WLA in meters MLLW, LMSL and  NAVD-88 as follows:

COOPS-ID, SHEF-ID, lon, lat, MLLW (meter), LMSL (meter), NAVD88 (feet)
        
@author: Jaime.Calzada@noaa.gov
"""

import datetime as dt
from collections import defaultdict
import pickle
import numpy as np
import csv
import os,sys
import csdldata
 
#------------------------------------------------------------------------------
def parse_shef(time_list):
    dicts= defaultdict(lambda: defaultdict(list))
    for kk in range(len(time_list)):
        try:
            shefpath = '/dcom/us007003/'+time_list[kk]+'/wtxtbul/tide_shef'
            
            with open(shefpath,'r') as inF:
                print('[info]: Reading directory: ' + shefpath)
                for line in inF:
                    if '.E ' in line:
                        station = line[3:8]
                        line2   = line[39:]
                        sdate    = dt.datetime(int(line[9:13]),int(line[13:15]), \
                        int(line[15:17]),int(line[22:24]),int(line[24:26]))
                        line2=line2.rstrip('\n')
                        fields = line2.split('/')
                        fields = [float(i) for i in fields]
                        for ii in range(len(fields)):
                            dicts[station][sdate].append(fields[ii])
                            if (len(fields) > 1):
                                sdate = sdate + dt.timedelta(minutes=6)
                    elif '.E1' in line:
                        line = line[3:]
                        line = line.rstrip('\n')
                        fields = line.split('/')
                        fields = [float(i) for i in fields]
                        for ii in range(len(fields)):
                            dicts[station][sdate].append(fields[ii])
                            if (len(fields) > 1):
                                sdate = sdate + dt.timedelta(minutes=6)
        except:
            print('[warn]: Directory not found: ' + shefpath)
            continue
    if not dicts:
        sys.exit('[error]: Couldn\'t find any files to parse!')
    return dicts
#------------------------------------------------------------------------------
def load_id_lookup_table():
    """" Loads the ID lookup table """
    dpath = csdldata.set_data_path()
    with open(dpath +'id_lookup_table.pkl', 'rb') as f:
        return pickle.load(f)
#------------------------------------------------------------------------------
def load_meter_mllw_to_msl():
    """" Loads the ID lookup table """
    dpath = csdldata.set_data_path()
    with open(dpath + 'meter_mllw_to_msl.pkl', 'rb') as f:
        return pickle.load(f)
#------------------------------------------------------------------------------
def load_feet_mllw_to_navd88():
    """" Loads the ID lookup table """
    dpath = csdldata.set_data_path()
    with open(dpath + 'feet_mllw_to_feet_navd88.pkl', 'rb') as f:
        return pickle.load(f)
#------------------------------------------------------------------------------
def time_list():
    base = dt.date.today() #- dt.timedelta(days=1)
    date_list = [base - dt.timedelta(days=x) for x in range(0,14)]
    date_list.reverse()
    time_list = [x.strftime("%Y%m%d") for x in date_list]
    return time_list
#------------------------------------------------------------------------------
def QC(shef):
    print('[info]: Removing invalid data points')
    shef_qc = defaultdict(lambda: defaultdict(np.array))
    stations = shef.keys()
    for i in range(len(stations)):
        keyss = shef[stations[i]].keys()
        for j in range(len(keyss)):
            val = np.array(shef[stations[i]][keyss[j]])
            val[val==-9999.0]=np.nan
            val = min(val)
            shef_qc[stations[i]][keyss[j]]=val
    return shef_qc
#------------------------------------------------------------------------------
def generate_bias_list(shef):
    print('[info]: Calculating bias from data')
    data = defaultdict(lambda: defaultdict(list))
    sbias_meter_msl,stat_m_msl,days_on_ts = bias_meter_msl(shef)
#    sbias_meter_msl = bias_meter_msl(shef)
    sbias_meter_mllw = bias_meter_mllw(shef)
    sbias_feet_navd88 = bias_feet_navd88(shef)
    ids = load_id_lookup_table()
    keyss = shef.keys()
#    print('Organizing data in dictionary')
    for i in range(len(keyss)):
        if keyss[i] in sbias_meter_msl and keyss[i] in sbias_feet_navd88:
            data[keyss[i]]['COOPS-ID']=ids[keyss[i]]['COOPS-ID']
            data[keyss[i]]['SHEF-ID']=ids[keyss[i]]['SHEF-ID']
            data[keyss[i]]['lon']=ids[keyss[i]]['lon']
            data[keyss[i]]['lat']=ids[keyss[i]]['lat']
            data[keyss[i]]['Bias_m_MLLW']=sbias_meter_mllw[keyss[i]]
            data[keyss[i]]['Bias_m_MSL']=sbias_meter_msl[keyss[i]]
            data[keyss[i]]['Bias_feet_NAVD88']=sbias_feet_navd88[keyss[i]]
            data[keyss[i]]['Statistical Significance']=stat_m_msl[keyss[i]]
            data[keyss[i]]['Total length of time series (days)']=days_on_ts[keyss[i]]
    return data
#------------------------------------------------------------------------------
def calc_stat_sig(data):
    
    start = min(data.keys())
    end = max(data.keys())
    len_data = sum(~np.isnan(data.values()))
    
    total_time = (end-start).seconds + ((end-start).days * 24 * 3600)
    days = (end-start).days + (end-start).seconds/(60.*60.*24)
    total_points = total_time/60
    total_points = (total_points/6)+1
    stat_sig = float(len_data)/float(total_points)
    return stat_sig, days
#------------------------------------------------------------------------------
def bias_meter_msl(shef):
    shef_meter_msl = defaultdict(np.array)
    stats=defaultdict(np.array)
    days_on_ts=defaultdict(np.array)
    convert_table = load_meter_mllw_to_msl()
    stations = shef.keys()
        
    for i in range(len(stations)):
	try:
            val = np.array(shef[stations[i]].values())
            val = val[~np.isnan(val)]
            val = np.mean(val)
            val_meter_mllw = np.multiply(0.3048,val)
            num = float(convert_table[stations[i]]['factor'])
            if num != -999999.0:
                val_meter_msl  = float(val_meter_mllw) + num
                shef_meter_msl[stations[i]] = val_meter_msl
                stat_sig, length_of_ts = calc_stat_sig(shef[stations[i]])
                stats[stations[i]] = stat_sig
                days_on_ts[stations[i]] = length_of_ts
        except:
	    print '[warn]: station is not in vdatum ', stations[i]

    return shef_meter_msl, stats, days_on_ts
#------------------------------------------------------------------------------
def bias_meter_mllw(shef):
    shef_meter_mllw = defaultdict(np.array)
    stations = shef.keys()
    for i in range(len(stations)):
        val = np.array(shef[stations[i]].values())
        val = val[~np.isnan(val)]
        val = np.mean(val)
        val_meter_mllw = np.multiply(0.3048,val)
        shef_meter_mllw[stations[i]] = float(val_meter_mllw)
    return shef_meter_mllw
#------------------------------------------------------------------------------
def bias_feet_navd88(shef):
    shef_feet_navd88 = defaultdict(np.array)
    convert_table = load_feet_mllw_to_navd88()
    stations = shef.keys()
    for i in range(len(stations)):
        try:
            val = np.array(shef[stations[i]].values())
            val = val[~np.isnan(val)]
            val = np.mean(val)
            num = float(convert_table[stations[i]]['factor'])
            if num != -999999.0:
                val_feet_navd88 = float(val) + num
                shef_feet_navd88[stations[i]] = val_feet_navd88
        except:
            print '[warn]: station not in vdatum list ', stations[i] 
    return shef_feet_navd88
#------------------------------------------------------------------------------
def write_bias_file(shef, csvFile):
    data = generate_bias_list(shef)
    print('Writing data to: '+ csvFile)
    
    with open(csvFile,'wb') as f:
        header=['COOPS-ID','SHEF-ID','lon','lat','Bias MLLW (meters)', \
        'Bias MSL (meters)', 'Bias NAVD88 (feet)','Statistical Significance', \
        'Total length of record in days']
        writer = csv.writer(f)
        writer.writerow(header)
        keyss = data.keys()
        for i in range(len(data)):
            line = [data[keyss[i]]['COOPS-ID'],data[keyss[i]]['SHEF-ID'], \
            data[keyss[i]]['lon'],data[keyss[i]]['lat'], \
            data[keyss[i]]['Bias_m_MLLW'], \
            data[keyss[i]]['Bias_m_MSL'], \
            data[keyss[i]]['Bias_feet_NAVD88'],\
            data[keyss[i]]['Statistical Significance'],\
            data[keyss[i]]['Total length of time series (days)']]
            writer.writerow(line)
    print('[info]: Total number of sations written to file: ' + str(len(keyss)))
#------------------------------------------------------------------------------

def read_shef():
    """ Reads water level observations from WCOSS data bank;
        Converts from MLLW feet to LMSL meters
     """
    print '[info]: Reading water levels from SHEF data bank, converting to LMSL.'
    shef = parse_shef(time_list())
    shef = QC(shef)
    data = generate_bias_list(shef)
    convert_table = load_meter_mllw_to_msl()
    obs=defaultdict(lambda: defaultdict(list))

    for item in data.keys():
        ids =  data[item]['COOPS-ID']
        obs[ids]['NWS_ID'] = data[item]['SHEF-ID']
        obs[ids]['lon'] = data[item]['lon']
        obs[ids]['lat'] = data[item]['lat']
        obs[ids]['dates'] = shef[item].keys()
        num = float(convert_table[item]['factor'])
        obs[ids]['values'] = np.multiply(0.3048,shef[item].values()) + num
    return obs

#------------------------------------------------------------------------------
def bias_table(fileToSave):

    print '[info]: Creating table of waterlevel biases based on SHEF databank.'
    shef  = parse_shef(time_list())
    shef = QC(shef) 
    write_bias_file(shef, fileToSave)












