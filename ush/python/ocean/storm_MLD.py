"""

 storm_MLD.py
 -------------
    read a HYCOM 3z .nc file,
    extract OHC and plot in time series.


 ***************************************************************************
usage: python storm_MLD.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 ***************************************************************************


 HISTORY
 -------
    modified to comply the convention of number of input argument and
       graphic filename. -hsk 8/2020
    modified so to read in a set of HYCOM *.nc files. -hsk 7/17/2020
    modified to take global varibles from kick_graphics.py -hsk 9/20/2018
    modified to fit for RT run by Hyun-Sook Kim 5/17/2017
    edited by Hyun-Sook Kim 9/18/2015
    modified by Hyun-Sook Kim 11/18/2016
---------------------------------------------------------------
"""
import sys
#sys.path.insert(0,'/lfs4/HFIP/hwrfv3/Hyun.Sook.Kim/myconda')

from utils4HWRF import readTrack6hrly
from utils import coast180, find_dist

import os
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

print("code:   storm_MLD.py")

cx,cy=coast180()
if tcid[-1].lower() == 'l' or tcid[-1].lower() == 'e' or tcid[-1].lower() == 'c':
    cx=cx+360

if tcid[-1].lower()=='l':
   aprefix=storm.lower()+tcid.lower()+'.'+cycle
   nprefix='natl00l.'+cycle+'.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   aprefix=storm.lower()+tcid.lower()+'.'+cycle
   nprefix='epac00l.'+cycle+'.hafs_hycom_hep10'

atcf = COMOUT+'/'+aprefix+'.trak.'+model.lower()+'.atcfunix'

#------------------------------------------------------------------------------------
# - get MLD  *_3z_*.[nc] files
#
Rkm=500 	# search radius
# prefix for  rtofs*.[ab] files
afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)

var=ncfiles['mixed_layer_thickness']
dvar=var-var[0]

lns,lts=np.meshgrid(var['Longitude'],var['Latitude'])
dummy=np.ones(lns.shape)

adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
    aln=[-1*a+360 for a in aln]

for k in range(len(aln)):

   dR=find_dist(lns,lts,aln[k],alt[k])
   dumb=dummy.copy()
   dumb[dR>Rkm]=np.nan

   fhr=k*6
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+' '+tcid.upper()+'  '+'Ver Hr '+"%03d"%(fhr)+'  (IC='+cycle+'): MLD & Change [m]',fontsize=15)
   plt.subplot(121)
   (var[k]*dumb).plot.contourf(levels=np.arange(0,85,5),vmin=0,vmax=90,cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var[k]*dumb)+","+"%6.1f)"%np.nanmin(var[k]*dumb)
   plt.text(aln[k]-5.25,alt[k]-5.35,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

   plt.subplot(122)
   (dvar[k]*dumb).plot.contourf(levels=np.arange(-30,30,5),vmin=-30,vmax=30,cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar[k]*dumb)+","+"%6.1f)"%np.nanmin(dvar[k]*dumb)
   plt.text(aln[k]-5.25,alt[k]-5.35,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.MLD.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close("all")

# --- successful exit
sys.exit(0)
#end of script

