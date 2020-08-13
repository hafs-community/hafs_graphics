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
from utils import coast180, find_dist

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

print("code:   storm_TempZ100m.py")

cx,cy=coast180()

if tcid[-1].lower()=='l':
   nprefix='natl00l.'+cycle+'.hafs_hycom_hat10'
if tcid[-1].lower()=='e':
   nprefix='epac00l.'+cycle+'.hafs_hycom_hep10'

aprefix=storm.lower()+tcid.lower()+'.'+cycle
atcf = COMOUT+'/'+aprefix+'.trak.'+model.lower()+'.atcfunix'

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

if tcid[-1].lower()=='l':
   xindx=np.arange(563,3661,2)
   yindx=np.arange(648,1980,2)

xnc=xr.open_mfdataset(nfiles)
var1=xnc['LHTFL_surface'].isel(longitude=xindx,latitude=yindx)
var2=xnc['SHTFL_surface'].isel(longitude=xindx,latitude=yindx)

del nfiles

lns,lts=np.meshgrid(var1['longitude'],var1['latitude'])
dummy=np.ones(lns.shape)

adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
if tcid[-1].lower()=='l' or tcid[-1].lower()=='e':
    aln=[-1*a for a in aln]

for k in range(len(aln)):
   dR=find_dist(lns,lts,aln[k],alt[k])
   R=find_dist(lns,lts,aln[k],alt[k])
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
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var1[k]*dumb)+","+"%6.1f)"%np.nanmin(var1[k]*dumb)
   plt.text(aln[k]-5.25,alt[k]-4.25,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

   plt.subplot(122)
   dvar=(var1[k]-var1[0])*dumb
   dvar.plot.contourf(levels=np.arange(-500,550,50),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-5.25,alt[k]-4.25,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

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
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var2[k]*dumb)+","+"%6.1f)"%np.nanmin(var2[k]*dumb)
   plt.text(aln[k]-5.25,alt[k]-4.25,mnmx,fontsize=14,color='r',fontweight='bold')
   plt.subplot(122)
   dvar=(var2[k]-var2[0])*dumb
   dvar.plot.contourf(levels=np.arange(-200,225,25),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-5.25,alt[k]-5.4,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

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

   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(var0*dumb)+","+"%6.1f)"%np.nanmin(var0*dumb)
   plt.text(aln[k]-5.25,alt[k]-5.4,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')
   plt.subplot(122)
   dvar=(var0-var1[0]-var2[0])*dumb
   dvar.plot.contourf(levels=np.arange(-100,1150,50),cmap='bwr')
   plt.plot(cx,cy,color='gray')
   if trackon[0].lower()=='y':
        plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2)
        plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6)
   plt.axis([aln[k]-5.5,aln[k]+4.5,alt[k]-5.5,alt[k]+4.5])
   mnmx="(min,max)="+"(%6.1f"%np.nanmax(dvar)+","+"%6.1f)"%np.nanmin(dvar)
   plt.text(aln[k]-5.25,alt[k]-5.4,mnmx,fontsize=14,color='DarkOliveGreen',fontweight='bold')

   pngFile=os.path.join(graphdir,aprefix.upper()+'.'+model.upper()+'.storm.TurbFlux.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight')

   plt.close('all')

# remove temporary directory
#shutil.rmtree(nctmp)

# --- successful exit
sys.exit(0)
#end of script


