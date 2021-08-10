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

cx_hycom = np.asarray([cx+360 if cx<74.16 else cx for cx in np.asarray(cx)])
cy_hycom = cy

aprefix=storm.lower()+tcid.lower()+'.'+cycle
if tcid[-1].lower()=='l':
   nprefix = aprefix + '.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   nprefix = aprefix + '.hafs_hycom_hep20'
if tcid[-1].lower()=='w':
   nprefix = aprefix + '.hafs_hycom_hwp30'
if tcid[-1].lower()=='c':
   nprefix = aprefic + '.hafs_hycom_hcp70'

if trackon[0].lower()=='y':
   gatcf = glob.glob(COMOUT+'/*.atcfunix.all')
   if gatcf:
      trackon = 'yes'
   else:
      trackon = 'no'

#   ------------------------------------------------------------------------------------
# - get Z20  *_3z_*.[nc] files
#
# prefix for  rtofs*.[ab] files
#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))

ncfiles=xr.open_mfdataset(afiles)

varr = ncfiles['depth of 20C isotherm']
dvarr = varr-varr[0]
var_name = 'Z20'
units = '(m)'
delta_var = 10

for k in range(varr.shape[0]):

   lon = np.asarray(varr[k].Longitude)
   lat = np.asarray(varr[k].Latitude)
   lon_geo = np.asarray([ln-360 if ln>=180 else ln for ln in lon])
   lat_geo = lat
   var = np.asarray(varr[k])
   dvar = np.asarray(dvarr[k])

   fhr=k*6
   fig=plt.figure(figsize=(15,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%3d"%(fhr)+'  (IC='+cycle+'): '+var_name + ' & Change '+units,fontsize=15)

   ax121=plt.subplot(121)
   kw = dict(levels=np.arange(np.floor(np.nanmin(var)),np.ceil(np.nanmax(var)),delta_var))
   #var[k].plot.contourf(levels=np.arange(18,32,0.5),cmap='RdBu_r')
   plt.contourf(lon,lat,var,cmap='RdYlBu',**kw)
   cbar = plt.colorbar()
   cbar.set_label(units,fontsize=14)
   plt.plot(cx_hycom,cy_hycom,'.',color='gray',markersize=2)
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         aln_hycom = np.asarray([ln+360 if ln<74.16 else ln for ln in aln])
         alt_hycom = alt
         plt.plot(aln_hycom,alt_hycom,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln_hycom[k],alt_hycom[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   plt.axis([lon[0],lon[-1],lat[0],lat[-1]])
   xticks =  np.arange(np.round(lon[0],-1),np.round(lon[-1],-1),20)
   xticklabel_geo = np.asarray([str(xt-360) if xt>=180 else str(xt) for xt in xticks])
   ax121.set_xticks(xticks)
   ax121.set_xticklabels(xticklabel_geo)
   ax121.set_aspect('equal')
   plt.ylabel('Latitude',fontsize=14)
   plt.xlabel('Longitude',fontsize=14)

   ax122=plt.subplot(122)
   dvl = np.round(np.max([np.abs(np.nanmin(dvar)),np.abs(np.nanmax(dvar))]),0)
   if dvl == 0.0:
       kw = dict(levels=np.arange(-4,4.1,1))
   else:
       kw = dict(levels=np.linspace(-dvl,dvl,dvl+1))
   #var[k].plot.contourf(levels=np.arange(18,32,0.5),cmap='RdBu_r')
   plt.contourf(lon,lat,dvar,cmap='bwr',**kw)
   cbar = plt.colorbar()
   cbar.set_label(units,fontsize=14)
   plt.plot(cx_hycom,cy_hycom,'.',color='gray',markersize=2)
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)
         aln_hycom = np.asarray([ln+360 if ln<74.16 else ln for ln in aln])
         alt_hycom = alt
         plt.plot(aln_hycom,alt_hycom,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln_hycom[k],alt_hycom[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   plt.axis([lon[0],lon[-1],lat[0],lat[-1]])
   xticks =  np.arange(np.round(lon[0],-1),np.round(lon[-1],-1),20)
   xticklabel_geo = np.asarray([str(xt-360) if xt>=180 else str(xt) for xt in xticks])
   ax122.set_xticks(xticks)
   ax122.set_xticklabels(xticklabel_geo)
   ax122.set_aspect('equal')
   plt.ylabel('Latitude',fontsize=14)
   plt.xlabel('Longitude',fontsize=14)

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.'+var_name+'.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight',pad_inches=0.2)

   plt.close("all")

# --- successful exit
sys.exit(0)
#end of script

