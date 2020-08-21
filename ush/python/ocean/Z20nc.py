"""

 Z20nc.py
 -------------
    read a HYCOM surface archive .[ab] file,
    extract Z20 and plot in time series.


 *************************************************************************
 usage: python Z20nc.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 *************************************************************************


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
from utils import coast180

import os
import sys
import glob
import xarray as xr

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
  
from pathlib import Path

plt.switch_backend('agg')

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

print("code:   Z20nc.py")

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
   gatcf = glob.glob('*.atcfunix')
   if gatcf:
      trackon='yes'
   else:
      trackon='no'

if tcid[-1].lower() == 'l' or tcid[-1].lower() == 'e' or tcid[-1].lower() == 'c':
    cx=cx+360

#   ------------------------------------------------------------------------------------
# - get Z20  *_3z_*.[nc] files
#
# prefix for  rtofs*.[ab] files
#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)

var=ncfiles['depth of 20C isotherm']
dvar=var-var[0]
for k in range(var.shape[0]):
   fhr=k*6
   fig=plt.figure(figsize=(15,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%3d"%(fhr)+'  (IC='+cycle+'): \n Z20 & Change [m]',fontsize=15)
   ax121=plt.subplot(121)
   vark=var[k].where(var[k]>2,np.nan)
   vark.plot.contourf(levels=np.arange(0,260,10),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
            aln=-1*aln+360
         plt.plot(aln,alt,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   #plt.axis([262,320,5,45])
   plt.axis([var.Longitude[0],var.Longitude[-1],var.Latitude[0],var.Latitude[-1]])
   ax121.set_aspect('equal')
   ax122=plt.subplot(122)
   dvar[k].plot.contourf(levels=np.arange(-15,17.5,2.5),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
            aln=-1*aln+360
         plt.plot(aln,alt,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   #plt.axis([262,320,5,45])
   plt.axis([var.Longitude[0],var.Longitude[-1],var.Latitude[0],var.Latitude[-1]])
   ax122.set_aspect('equal')

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.Z20.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight',pad_inches=0.2)

   plt.close("all")

# --- successful exit
sys.exit(0)
#end of script

