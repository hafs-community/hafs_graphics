"""

 SSTnc.py
 -------------
    read a HYCOM surface archive .[ab] file,
    extract SST and plot in time series.


 ************************************************************************
 usage: python SSTnc.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 ************************************************************************


 HISTORY
 -------
    modified to comply the convention of number of input argument and 
       graphic filename. -hsk 8/2020
    modified to take global varibles from kick_graphics.py -hsk 9/20/2018
    modified to fit for RT run by Hyun-Sook Kim 5/17/2017
    edited by Hyun-Sook Kim 9/18/2015
    modified by Hyun-Sook Kim 11/18/2016
---------------------------------------------------------------
"""

from utils4HWRF import readTrack6hrly
from utils import coast180, find_dist

import os
import sys
import glob
import xarray as xr

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
  
from pathlib import Path

#plt.switch_backend('agg')

#================================================================
model =sys.argv[1]
storm = sys.argv[2]
tcid = sys.argv[3]
cycle = sys.argv[4]
trackon = sys.argv[5]
COMOUT = sys.argv[6]

graphdir = sys.argv[7]
if not os.path.isdir(graphdir):
      p=Path(graphdir)
      p.mkdir(parents=True)

print("code:   SSTnc.py")

cx,cy=coast180()

#-- atcfunix first
if tcid[-1].lower()=='l':
   aprefix=storm.lower()+tcid.lower()+'.'+cycle
   nprefix=aprefix+'.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   aprefix=storm.lower()+tcid.lower()+'.'+cycle
   nprefix=aprefix+'.hafs_hycom_hep10'

#nan1d=np.nan*np.empty([22,1])
if trackon[0].lower()=='y':
   gatcf = glob.glob(COMOUT+'/*.atcfunix')

if tcid[-1].lower() == 'l' or tcid[-1].lower() == 'e' or tcid[-1].lower() == 'c':
    cx=cx+360

#   ------------------------------------------------------------------------------------
# - get SST  *_3z_*.[nc] files
#
# prefix for  rtofs*.[ab] files
afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)

var=ncfiles['temperature'].isel(Z=0)
dvar=var-var[0]
for k in range(var.shape[0]):
   fhr=k*6
   fig=plt.figure(figsize=(15,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%3d"%(fhr)+'  (IC='+cycle+'): \n SST & Change [$^o$C]',fontsize=15)
   plt.subplot(121)
   var[k].plot.contourf(levels=np.arange(18,32,0.5),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
            aln=-1*aln+360
         plt.plot(aln,alt,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   plt.axis([262,320,5,45])
   plt.subplot(122)
   dvar[k].plot.contourf(levels=np.arange(-4,3.5,0.5),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
            aln=-1*aln+360
         plt.plot(aln,alt,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   plt.axis([262,320,5,45])
   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.SST.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight',pad_inches=0.2)

   plt.close("all")

# --- successful exit
sys.exit(0)
#end of script
