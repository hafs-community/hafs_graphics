"""

 storm_OHC.py
 -------------
    read a HYCOM surface archive .[ab] file,
    extract 26oC isotherm and plot footprint Z20 and temporal variation 
    on the footprint (R<=500 km).


 ****************************************************************************
 usage: python storm_OHC.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 ****************************************************************************

 HISTORY
 -------
    modified to comply the convention of number of input argument and
       graphic filename. -hsk 8/2020
    modified, so to read in *.nc files. -hsk 7/16/2020.
    modified by HSK 9/19/2018 for multi-processing use
    by Hyun-Sook Kim 3/1/2017
---------------------------------------------------------------
"""
import sys
#sys.path.insert(0,'/lfs4/HFIP/hwrfv3/Hyun.Sook.Kim/myconda')

from utils4HWRF import readTrack6hrly
from utils import coast180
from geo4HYCOM import haversine


import xarray as xr
from datetime import datetime, timedelta

import os
import glob

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

print("code:   storm_OHC.py")

cx,cy=coast180()
if tcid[-1].lower() == 'l' or tcid[-1].lower() == 'e' or tcid[-1].lower() == 'c':
    cx=cx+360

if tcid[-1].lower()=='l':
   nprefix=model.lower()+tcid.lower()+'.'+cycle+'.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   nprefix=model.lower()+tcid.lower()+'.'+cycle+'.hafs_hycom_hep20'
if tcid[-1].lower()=='w':
   nprefix=model.lower()+tcid.lower()+'.'+cycle+'.hafs_hycom_hwp30'
if tcid[-1].lower()=='c':
   nprefix=model.lower()+tcid.lower()+'.'+cycle+'.hafs_hycom_hcp70'

aprefix=storm.lower()+tcid.lower()+'.'+cycle
atcf = aprefix+'.trak.'+model.lower()+'.atcfunix'

# ------------------------------------------------------------------------------------
Rkm=500         # search radius
#
# - get OHC0 from *basin.yyyy_yrday_hh.nc (generated from rtofs_archv3z2nc (new hafs_ab2data codes)
# prefix for  rtofs*.[ab] files
#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))

# - get OHC from each *.nc files
ncfiles=xr.open_mfdataset(afiles)

var=ncfiles['ocean_heat_content']
dvar=var-var[0]

lns,lts=np.meshgrid(var['Longitude'],var['Latitude'])
dummy=np.ones(lns.shape)
#stats=[]                # (mean,min,max) for MLD
                        # and (mean,min.max) for MLD change
adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
    aln=[a+360 for a in aln]

for k in range(len(aln)):

   dR=haversine(lns,lts,aln[k],alt[k])/1000.
   dumb=dummy.copy()
   dumb[dR>Rkm]=np.nan

   fhr=k*6
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+' '+tcid.upper()+'  '+'Ver Hr '+"%3d"%(fhr)+'  (IC='+cycle+'): OHC & Change [kJ/cm$^2$]',fontsize=15)
   plt.subplot(121)
   vark=var[k].where(var[k].values > 2,np.nan)
   (var[k]*dumb).plot.contourf(levels=np.arange(0,165,5),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var[k]*dumb)+","+"%6.1f)"%np.nanmin(var[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   plt.subplot(122)
   (dvar[k]*dumb).plot.contourf(levels=np.arange(-80,80,10),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar[k]*dumb)+","+"%6.1f)"%np.nanmin(dvar[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])


   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.OHC.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.savefig(pngFile)
   plt.close("all")

# --- successful exit
sys.exit(0)
#-------------------------------------------------------------------------
