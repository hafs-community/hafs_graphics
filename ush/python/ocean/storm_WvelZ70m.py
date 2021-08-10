"""

 WvelZ70m.py
 -------------
    read a HYCOM surface archive .[ab] file,
    extract SST and plot in time series.

 *********************************************************************************
 usage: python storm_WvelZ70m.py stormModel stormName stormID YMDH trackon COMhafs
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

print("code:   storm_WvelZ70m.py")

cx,cy=coast180()

cx_hycom = np.asarray([cx+360 if cx<74.16 else cx for cx in np.asarray(cx)])
cy_hycom = cy

aprefix = storm.lower()+tcid.lower()+'.'+cycle
if tcid[-1].lower()=='l':
   nprefix = aprefix + '.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   nprefix = aprefix + '.hafs_hycom_hep20'
if tcid[-1].lower()=='w':
   nprefix = aprefix + '.hafs_hycom_hwp30'
if tcid[-1].lower()=='c':
   nprefix = aprefic + '.hafs_hycom_hcp70'

atcf = glob.glob(COMOUT+'/*.atcfunix.all')[0]

#------------------------------------------------------------------------------------
# - get SST  *_3z_*.[nc] files
#
Rkm=500    # search radius [km]

# prefix for  rtofs*.[ab] files
#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)

adt,aln,alt,pmn,vmx = readTrack6hrly(atcf)
aln_hycom = np.asarray([ln+360 if ln<74.16 else ln for ln in aln])
alt_hycom = alt

varr = ncfiles['w_velocity'].isel(Z=12)
dvarr = varr-varr[0]
var_name = '70 m Wvel'
units = '(m/day)'
delta_var = 10

lns,lts = np.meshgrid(varr['Longitude'],varr['Latitude'])
dummy = np.ones(lns.shape)

skip = 3
u0 = ncfiles['u_velocity'].isel(Z=12)[:,::skip,::skip]
v0 = ncfiles['v_velocity'].isel(Z=12)[:,::skip,::skip]
ln = lns[::skip,::skip]
lt = lts[::skip,::skip]

del ncfiles

for k in range(len(aln)):

   dR=haversine(lns,lts,aln[k],alt[k])/1000.
   dumb=dummy.copy()
   dumb[dR>Rkm]=np.nan
   
   lon = np.asarray(varr[k].Longitude)
   lat = np.asarray(varr[k].Latitude)
   var = np.asarray(varr[k])*dumb
   dvar = np.asarray(varr[k]-varr[0])*dumb

   fhr=k*6

   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%03d"%(fhr)+'  (IC='+cycle+'): '+var_name+ ' & Change '+units,fontsize=15)

   ax121 = plt.subplot(121)
   #(var1[k]*dumb).plot.contourf(levels=np.arange(0,850,50),cmap='RdBu_r')
   kw = dict(levels=np.arange(np.floor(np.nanmin(var)),np.round(np.nanmax(var),1)+delta_var,delta_var))
   plt.contourf(lon,lat,var,cmap='RdYlBu_r',**kw)
   cbar = plt.colorbar()
   cbar.set_label(units,fontsize=14)
   plt.plot(cx_hycom,cy_hycom,'.',color='gray',markersize=2)
   if trackon[0].lower()=='y':
        plt.plot(aln_hycom,alt_hycom,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln_hycom[k],alt_hycom[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmin(var)+","+"%6.1f)"%np.nanmax(var)
   plt.text(aln_hycom[k]-4.25,alt_hycom[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5))
   plt.axis([aln_hycom[k]-5.5,aln_hycom[k]+5.5,alt[k]-5,alt[k]+5])
   q=plt.quiver(ln,lt,u0.isel(MT=k),v0.isel(MT=k),scale=700)
   xticks =  np.arange(np.round(aln_hycom[k]-5.5,0),np.round(aln_hycom[k]+5.5,0),2)
   xticklabel_geo = np.asarray([str(xt-360) if xt>=180 else str(xt) for xt in xticks])
   ax121.set_xticks(xticks)
   ax121.set_xticklabels(xticklabel_geo)
   ax121.set_aspect('equal')
   plt.ylabel('Latitude',fontsize=14)
   plt.xlabel('Longitude',fontsize=14)

   ax122 = plt.subplot(122)
   dvl = np.round(np.max([np.abs(np.nanmin(dvar)),np.abs(np.nanmax(dvar))]),0)
   if dvl == 0.0:
       kw = dict(levels=np.arange(-30,31,5))
   else:
       kw = dict(levels=np.linspace(-dvl,dvl,dvl+1))
   plt.contourf(lon,lat,dvar,cmap='bwr',**kw)
   cbar = plt.colorbar()
   cbar.set_label(units,fontsize=14)
   #dvar.plot.contourf(levels=np.arange(-500,550,50),cmap='bwr')
   plt.plot(cx_hycom,cy_hycom,'.',color='gray',markersize=2)
   if trackon[0].lower()=='y':
        plt.plot(aln_hycom,alt_hycom,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln_hycom[k],alt_hycom[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmin(dvar)+","+"%6.1f)"%np.nanmax(dvar)
   plt.text(aln_hycom[k]-4.25,alt_hycom[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5))
   plt.axis([aln_hycom[k]-5.5,aln_hycom[k]+5.5,alt[k]-5,alt[k]+5])
   xticks =  np.arange(np.round(aln_hycom[k]-5.5,0),np.round(aln_hycom[k]+5.5,0),2)
   xticklabel_geo = np.asarray([str(xt-360) if xt>=180 else str(xt) for xt in xticks])
   ax122.set_xticks(xticks)
   ax122.set_xticklabels(xticklabel_geo)
   ax122.set_aspect('equal')
   plt.ylabel('Latitude',fontsize=14)
   plt.xlabel('Longitude',fontsize=14)

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.Wvel.Z70m.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   #plt.close("all")

# --- successful exit
sys.exit(0)
#end of script

