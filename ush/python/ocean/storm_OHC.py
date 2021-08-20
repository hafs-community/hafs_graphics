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

atcf = COMOUT+'/' + storm + tcid + '.' + cycle + '.trak.' + model + '.atcfunix'

# ------------------------------------------------------------------------------------
Rkm=500         # search radius
#
# - get OHC0 from *basin.yyyy_yrday_hh.nc (generated from rtofs_archv3z2nc (new hafs_ab2data codes)
# prefix for  rtofs*.[ab] files
#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'*3z*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))

# - get OHC from each *.nc files
ncfiles=xr.open_mfdataset(afiles)

adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
aln_hycom = np.asarray([ln+360 if ln<74.16 else ln for ln in aln])
alt_hycom = alt

varr = ncfiles['ocean_heat_content']
dvarr = varr-varr[0]
var_name = 'OHC'
units = '($kJ/cm^2$)'

lns,lts=np.meshgrid(varr['Longitude'],varr['Latitude'])
dummy=np.ones(lns.shape)

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
   kw = dict(levels=np.arange(0,166,5))
   #kw = dict(levels=np.arange(np.floor(np.nanmin(var)),np.round(np.nanmax(var),-1)+delta_var,delta_var))
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
   xticks =  np.arange(np.round(aln_hycom[k]-5.5,0),np.round(aln_hycom[k]+5.5,0),2)
   xticklabel_geo = np.asarray([str(xt-360) if xt>=180 else str(xt) for xt in xticks])
   ax121.set_xticks(xticks)
   ax121.set_xticklabels(xticklabel_geo)
   ax121.set_aspect('equal')
   plt.ylabel('Latitude',fontsize=14)
   plt.xlabel('Longitude',fontsize=14)

   ax122 = plt.subplot(122)
   kw = dict(levels=np.arange(-80,81,5))
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

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.OHC.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.savefig(pngFile)
   plt.close("all")


# --- successful exit
sys.exit(0)
#-------------------------------------------------------------------------
