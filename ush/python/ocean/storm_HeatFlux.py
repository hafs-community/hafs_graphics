"""

 storm_HeatFlux.py
 -----------------
    read a set of FV3 phyf*.nc file,
    extract latent heat fluxs,
    and reurn a series of graphics.


 *********************************************************************************
 usage: python storm_HeatFlux.py stormModel stormName stormID YMDH trackon COMhafs
 -----
 *********************************************************************************

 HISTORY
 -------
    modified to comply the convention of number of input argument and
       graphic filename. -hsk 8/2020
    modified so to read in a set of phyf*.nc files. -hsk 7/17/2020
    modified to take global varibles from kick_graphics.py -hsk 9/20/2018
    modified to fit for RT run by Hyun-Sook Kim 5/17/2017
    edited by Hyun-Sook Kim 9/18/2015
    modified by Hyun-Sook Kim 11/18/2016
---------------------------------------------------------------
"""

from utils4HWRF import readTrack, readTrack6hrly
from utils import coast180
from geo4HYCOM import haversine

import os, shutil
import sys
import glob
import xarray as xr

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
  
from pathlib import Path

import socket

plt.switch_backend('agg')

def ZoomIndex(var,aln,alt):
   """ find indices of the lower-left corner and the upper-right corner 
       of an area encompassing the predicted storm track.

       var: an xarray with longitude and latitude coordinate names
       aln,alt: a set of predicted TC locations (longitude,latitude).
   """
   aln = np.asarray(aln)
   alt = np.asarray(alt)
   minlon = np.min(aln) - 8
   maxlon = np.max(aln) + 8
   minlat = np.min(alt) - 8
   maxlat = np.max(alt) + 8

   lat = np.asarray(var.latitude)
   lon = np.asarray(var.longitude)

   # find an index for the lower-left corner
   xll = np.interp(minlon,lon,np.arange(len(lon))).astype(int)
   yll = np.interp(minlat,lat,np.arange(len(lat))).astype(int)

   # find an index for the upper-right corner
   xur = np.interp(maxlon,lon,np.arange(len(lon))).astype(int)
   yur = np.interp(maxlat,lat,np.arange(len(lat))).astype(int)

   '''
   # find an index for the lower-left corner
   abslat=np.abs(var.latitude-min(alt)-8)
   abslon=np.abs(var.longitude-min(aln)-8)
   c=np.maximum(abslon,abslat)
   ([xll],[yll])=np.where(c==np.min(c))

   # find an index for the upper-right corner
   abslon=np.abs(var.longitude-max(aln)+8)
   abslat=np.abs(var.latitude-max(alt)+8)
   c=np.maximum(abslon,abslat)
   ([xur],[yur])=np.where(c==np.min(c))
   '''

   xindx=np.arange(xll,xur,1)
   yindx=np.arange(yll,yur,1)
   
   return (xindx,yindx)
    
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

print("code:   storm_HeatFlux.py")

cx,cy=coast180()
#if tcid[-1].lower() == 'l' or tcid[-1].lower() == 'e' or tcid[-1].lower() == 'c':
#    cx=cx+360

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
# - preprocessing: subset and convert wgrib2 to netcdf

#
Rkm=500 	# search radius

scrubbase='./tmp/'

part=nprefix.partition('.'+model.lower()+'_')[0]
nctmp=os.path.join(scrubbase,part)
if os.path.isdir(nctmp):
   shutil.rmtree(nctmp)
p=Path(nctmp)
p.mkdir(parents=True)

# track
adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
#if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
#    aln=[-1*a + 360. for a in aln]

#afiles = sorted(glob.glob(os.path.join(COMOUT,nprefix+'phyf*.nc')))
afiles = sorted(glob.glob(os.path.join(COMOUT,'*'+model.lower()+'prs.synoptic*.grb2')))
afiles=afiles[::2]   # subset to 6 hourly intervals
flxvar=':(LHTFL|SHTFL):surface:'
for k,A in enumerate(afiles):
    fhr=int(A.partition('.0p03.')[-1][1:4])
    if fhr==0:
      xvars=flxvar+'anl:'
    else:
      xvars=flxvar+"%g"%(fhr)
   
    ncout=os.path.join(nctmp,'heatflx_f'+"%03g"%fhr+'.nc')
    cmd='sh ./xgrb2nc.sh '+'"'+xvars+'"'+' '+A+' '+ncout
    os.system(cmd)

nfiles=sorted(glob.glob(os.path.join(nctmp,'heatflx_*.nc')))
del afiles

xnc=xr.open_mfdataset(nfiles)
xii,yii=ZoomIndex(xnc.isel(time=[0]),aln,alt)
xindx=xii[::2]
yindx=yii[::2]

var1=xnc['LHTFL_surface'].isel(longitude=xindx,latitude=yindx)
var2=xnc['SHTFL_surface'].isel(longitude=xindx,latitude=yindx)

del nfiles
del xnc

lns,lts=np.meshgrid(var1['longitude'],var1['latitude'])
dummy=np.ones(lns.shape)

for k in range(len(aln)):
   dR=haversine(lns,lts,aln[k],alt[k])/1000.0
   dumb=dummy.copy()
   dumb[dR>Rkm]=np.nan

   fhr=k*6
   
   #--- latent heat flux 
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%03d"%(fhr)+'  (IC='+cycle+'):  Latent Heat Flux & Change [W/m$^2$]',fontsize=15)
   plt.subplot(121)
   (var1[k]*dumb).plot.contourf(levels=np.arange(0,850,50),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var1[k]*dumb)+","+"%6.1f)"%np.nanmin(var1[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   plt.subplot(122)
   dvar=(var1[k]-var1[0])*dumb
   dvar.plot.contourf(levels=np.arange(-500,550,50),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.LHTFlux.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close('all')
   #--- sensible heat flux
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%03d"%(fhr)+'  (IC='+cycle+'): Sensible Heat Flux & Change [W/m$^2$]',fontsize=15)
   plt.subplot(121)
   (var2[k]*dumb).plot.contourf(levels=np.arange(-50,275,25),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var2[k]*dumb)+","+"%6.1f)"%np.nanmin(var2[k]*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='r',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   plt.subplot(122)
   dvar=(var2[k]-var2[0])*dumb
   dvar.plot.contourf(levels=np.arange(-200,225,25),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.SHTFlux.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close('all')
   # --- total heat flux
   fig=plt.figure(figsize=(14,5))
   plt.suptitle(storm.upper()+tcid.upper()+'  '+'Ver Hr '+"%03d"%(fhr)+'  (IC='+cycle+'): Turbulence Heat Flux & Change [W/m$^2$]',fontsize=15)
   plt.subplot(121)
   var0=var1[k]+var2[k]
   (var0*dumb).plot.contourf(levels=np.arange(0,1150,50),cmap='RdBu_r')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var0*dumb)+","+"%6.1f)"%np.nanmin(var0*dumb)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   plt.subplot(122)
   dvar=(var0-var1[0]-var2[0])*dumb
   dvar.plot.contourf(levels=np.arange(-100,1150,50),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-4.25,alt[k]-4.75,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.axis([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5])

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.totalHeatFlux.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close('all')

# remove temporary directory
#shutil.rmtree(nctmp)

# --- successful exit
sys.exit(0)
#end of script


