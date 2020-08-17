"""

 storm_tempZ40m.py
 -------------
    read a HYCOM surface archive .[ab] file,
    extract SST and plot in time series.


 *********************************************************************************
 usage: python storm_tempZ40m.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 *********************************************************************************

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
from geo4HYCOM import haversine


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

print("code:   storm_TempZ40m.py")

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
atcf = COMOUT+'/'+aprefix+'.trak.'+model.lower()+'.atcfunix'

#------------------------------------------------------------------------------------
# - get SST  *_3z_*.[nc] files
#
Rkm=500    # search radius [km]

# prefix for  rtofs*.[ab] files
afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)
var=ncfiles['temperature'].isel(Z=9)
dvar=var-var[0]
lns,lts=np.meshgrid(var['Longitude'],var['Latitude'])

skip=3
u0=ncfiles['u_velocity'].isel(Z=9)[:,::skip,::skip]
v0=ncfiles['v_velocity'].isel(Z=9)[:,::skip,::skip]
ln=lns[::skip,::skip]
lt=lts[::skip,::skip]

del ncfiles
dummy=np.ones(lns.shape)

adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
    aln=[-1*a+360 for a in aln]

for k in range(len(aln)):
   dR=haversine(lns,lts,aln[k],alt[k])/1000.
   dumb=dummy.copy()
   dumb[dR>Rkm]=np.nan
   
   fhr=k*6
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%3d"%(fhr)+'  (IC='+cycle+'): 40-m Temp & Change [$^o$C]',fontsize=15)
   plt.subplot(121)
   (var[k]*dumb).plot.contourf(levels=14,vmin=20,vmax=33,extend='both',cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   q=plt.quiver(ln,lt,u0.isel(MT=k),v0.isel(MT=k),scale=700)
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var[k]*dumb)+","+"%6.1f)"%np.nanmin(var[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   plt.subplot(122)
   (dvar[k]*dumb).plot.contourf(levels=np.arange(-4,3.5,0.5),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar[k]*dumb)+","+"%6.1f)"%np.nanmin(dvar[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.Temp.Z40m.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close("all")

# --- successful exit
sys.exit(0)
#end of script

