#
import sys
#sys.path.insert(0,'/lfs4/HFIP/hwrfv3/Hyun.Sook.Kim/myconda')

from utils4HWRF import readTrack6hrly
from utils import coast180

import xarray as xr
from datetime import datetime, timedelta

import os
import glob

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path

#----------note-----
# The graphdir is defined inside the individual python script.
#graphdir='/mnt/lfs4/HFIP/hwrfv3/Hyun.Sook.Kim/hafsv0p1cpl_ocngraphics'



#-----------------
model='hafs'
storm='natl'
tcid='00l'
trackon='y'
cycle='2020081306'
COMhafs='/mnt/lfs1/HFIP/hwrfv3/Role.rthafsa/hafstmp/hafsv0p1acpl_202007/com/2020081306/00L'
graphdir='/lfs1/HFIP/hwrfv3/Hyun.Sook.Kim/hafsv0p1cpl_ocngraphics'

gatcf=glob.glob(COMhafs+'/*.atcfunix')

list_storms=[]
list_tcids=[]

if len(gatcf) >1:
   for m,G in enumerate(gatcf):
       tmp=G.partition(COMhafs)
      
       patcf0=tmp[-1].partition('.'+cycle)[0]
       patcf=patcf0.replace('/','')
       list_storms.append(patcf[:-3])
       list_tcids.append(patcf[-3:])
 
cdir=os.getcwd()

#---- produce basin-scale figures:
cmd='python '+cdir+'/SSTnc.py '+model+' '+storm+' '+tcid+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
os.system(cmd)

cmd='python '+cdir+'/MLDnc.py '+model+' '+storm+' '+tcid+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
os.system(cmd)

cmd='python '+cdir+'/OHCnc.py '+model+' '+storm+' '+tcid+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
os.system(cmd)

cmd='python '+cdir+'/Z20nc.py '+model+' '+storm+' '+tcid+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
os.system(cmd)


#---- produce storm-scale figures:
for m in range(len(list_storms)):
   cmd='python '+cdir+'/storm_SST.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_MLD.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_OHC.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_Z20.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)


   cmd='python '+cdir+'/storm_tempZ40m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_tempZ70m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_tempZ100m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)



   cmd='python '+cdir+'/storm_WvelZ40m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_WvelZ70m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)

   cmd='python '+cdir+'/storm_WvelZ100m.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)


   cmd='python '+cdir+'/storm_HeatFlux.py '+model+' '+list_storms[m]+' '+list_tcids[m]+' '+cycle+' '+trackon+' '+COMhafs+' '+graphdir
   os.system(cmd)


