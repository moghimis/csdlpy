# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 10:02:14 2017

@author: Sergey.Vinogradov
"""
import numpy as np
import netCDF4

#==============================================================================
def readGrid ( gridFile ):
    """
    Reads ADCIRC grid file
    
    Args:
        gridFile (str): full path to fort.14 file
    Returns:
        grid (dict): field names according to ADCIRC internal variables:
    http://adcirc.org/home/documentation/users-manual-v50/
    input-file-descriptions/adcirc-grid-and-boundary-information-file-fort-14/
    """
    print '[info]: Reading the grid from ' + gridFile + '.'
    f  = open(gridFile)
    
    myDesc     = f.readline().rstrip()
    myNE, myNP = map(int, f.readline().split())    
    print '[info]: Grid description ' + myDesc + '.'
    print '[info]: Grid size: NE= '   + str(myNE) + ', NP=' + str(myNP) + '.'

    myPoints   = np.zeros([myNP,3], dtype=float)
    myElements = np.zeros([myNE,3], dtype=int)
    
    print '[info]: Reading grid points...'
    for k in range(myNP):
        line            = f.readline().split()
        myPoints[k,0:2] = map(float, line[1:3])

    print '[info]: Reading grid elements...'
    for k in range(myNE):
        line              = f.readline().split()
        myElements[k,0:2] = map(int, line[2:4])
    
    myNOPE   = int(f.readline().split()[0])
    myNETA   = int(f.readline().split()[0])   
    myNVDLL  = np.zeros([myNOPE], dtype=int)
    myNBDV   = np.zeros([myNOPE, myNETA], dtype=int)
    
    print '[info]: Reading elevation-specified boundaries...'    
    for k in range(myNOPE):
        myNVDLL [k] = int(f.readline().split()[0])
        for j in range(myNVDLL[k]):
            myNBDV[k,j] = int(f.readline().strip())

    myNBOU = int(f.readline().split()[0])
    myNVEL = int(f.readline().split()[0])   
    myNVELL      = np.zeros([myNBOU], dtype=int)
    myIBTYPE     = np.zeros([myNBOU], dtype=int)
    myNBVV       = np.zeros([myNBOU, myNVEL], dtype=int)
    myBARLANHT   = np.zeros([myNBOU, myNVEL], dtype=float)
    myBARLANCFSP = np.zeros([myNBOU, myNVEL], dtype=float)
    myIBCONN     = np.zeros([myNBOU, myNVEL], dtype=int)
    myBARINHT    = np.zeros([myNBOU, myNVEL], dtype=float)
    myBARINCFSB  = np.zeros([myNBOU, myNVEL], dtype=float)
    myBARINCFSP  = np.zeros([myNBOU, myNVEL], dtype=float)
    myPIPEHT     = np.zeros([myNBOU, myNVEL], dtype=float)
    myPIPECOEF   = np.zeros([myNBOU, myNVEL], dtype=float)
    myPIPEDIAM   = np.zeros([myNBOU, myNVEL], dtype=float)
    
    print '[info]: Reading normal flow-specified boundaries...'    
    for k in range(myNBOU):
        line = f.readline().split()
        myNVELL[k]  = int(line[0])
        myIBTYPE[k] = int(line[1])
        
        for j in range(myNVELL[k]):
            line = f.readline().rstrip().split()            
            if myIBTYPE[k] in   [0,1,2,10,11,12,20,21,22,30]:
                myNBVV      [k,j] = int(line[0])
            elif myIBTYPE[k] in [3,13,23]:
                myNBVV      [k,j] = int  (line[0])
                myBARLANHT  [k,j] = float(line[1])
                myBARLANCFSP[k,j] = float(line[2])
            elif myIBTYPE[k] in [4,24]:
                myNBVV      [k,j] = int  (line[0])
                myIBCONN    [k,j] = int  (line[1])
                myBARINHT   [k,j] = float(line[2])
                myBARINCFSB [k,j] = float(line[3])
                myBARINCFSP [k,j] = float(line[4])
            elif myIBTYPE[k] in [5,25]:
                myNBVV      [k,j] = int  (line[0])
                myIBCONN    [k,j] = int  (line[1])
                myBARINHT   [k,j] = float(line[2])
                myBARINCFSB [k,j] = float(line[3])
                myBARINCFSP [k,j] = float(line[4])
                myPIPEHT    [k,j] = float(line[5])
                myPIPECOEF  [k,j] = float(line[6])
                myPIPEDIAM  [k,j] = float(line[7])

    f.close()
        
    return {'GridDescription'               : myDesc, 
            'NE'                            : myNE, 
            'NP'                            : myNP, 
            'Points'                        : myPoints, 
            'Elements'                      : myElements,
            'NETA'                          : myNETA, 
            'NOPE'                          : myNOPE,
            'ElevationBoundaries'           : myNBDV, 
            'NormalFlowBoundaries'          : myNBVV,
            'ExternalBarrierHeights'        : myBARLANHT,
            'ExternalBarrierCFSPs'          : myBARLANCFSP,
            'BackFaceNodeNormalFlow'        : myIBCONN,
            'InternalBarrierHeights'        : myBARINHT,
            'InternallBarrierCFSPs'         : myBARINCFSP,
            'InternallBarrierCFSBs'         : myBARINCFSB,            
            'CrossBarrierPipeHeights'       : myPIPEHT,
            'BulkPipeFrictionFactors'       : myPIPECOEF,            
            'CrossBarrierPipeDiameter'      : myPIPEDIAM
            }

#==============================================================================
def read2DField ( ncFile, ncVar ):  
    """
    Reads specified variable from the ADCIRC 2D netCDF output
    and grid points along with validation time.
    Args:
        'ncFile' (str): full path to netCDF file
        'ncVar'  (str): name of netCDF field
    Returns:
        dict: 'lon', 'lat', 'time', 'value', 'path', 'variable'
    """
    nc   = netCDF4.Dataset (ncFile)
    lon  = nc.variables['x'][:]
    lat  = nc.variables['y'][:]
    tim  = nc.variables['time'][:]
    fld  = nc.variables[ncVar][:]     
    return { 'lon' : lon, 'lat' : lat, 'time' : tim, 'value' : fld, 
            'path' : ncFile, 'variable' : ncVar}

#==============================================================================
def read2DField_ascii ( asciiFile ):
    """
    Reads ADCIRC 2D output file (e.g. mmaxele)
    Args:
        'asciiFile' (str): full path to ADCIRC 2D file in ASCII format
    Returns:
        value (np.array [NP, NS]), where NP - number of grid points, 
                                     and NS - number of datasets
    """
    print '[info]: Reading ASCII file ' + asciiFile + '.'
    f  = open(asciiFile)
    
    myDesc = f.readline().strip()
    print '[info]: Field description [' + myDesc + '].'
    line          = f.readline().split()    
    myNDSETSE     = int(line[0])
    myNP          = int(line[1])
#    myNSPOOLGE    = int(line[3])
#    myIRTYPE      = int(line[4])
#    dtdpXnspoolge = float(line[2])   
    line          = f.readline().split()
#    myTIME        = float(line[0])
#    myIT          = float(line[1])
    value = np.zeros([myNP,myNDSETSE], dtype=float)
    for s in range(myNDSETSE):
        for n in range(myNP):
            value[n,s] = float(f.readline().split()[1])    
    value = np.squeeze(value)
    
    return value 

#==============================================================================
def readControlFile ( controlFile ):
    """
    Reads ADCIRC control file
    """
    print '[error]: not yet implemented'
    return None

#==============================================================================
def readFort13 ( fort13file ):
    """
    Reads ADCIRC fort.13 file
    """
    print '[error]: not yet implemented'
    return None

#==============================================================================
def readFort14 ( fort14file ):
    """
    Reads ADCIRC fort.14 file
    """
    return readGrid (fort14file)

#==============================================================================
def readFort15 ( fort15file ):
    """
    Reads ADCIRC fort.15 file
    """
    return readControlFile (fort15file)

#==============================================================================
if __name__ == "__main__":
    
    gridFile = "fort.14"
    grid = readGrid ( gridFile )
    
    x = grid['Points'][:,0]
    y = grid['Points'][:,1]
    import matplotlib.pyplot as plt
    plt.plot(x, y,'k.')
    plt.title(grid['GridDescription'])
#
#    
    