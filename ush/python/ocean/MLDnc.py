"""

 MLDnc.py
 -------------
    read a HYCOM 3z .nc file,
    extract MLD and plot in time series.


 ************************************************************************
 usage: python MLDnc.py stormModel stormName stormID YMDH trackon COMhafs graphdir
 -----
 ************************************************************************


 HISTORY
 -------
    modified to implement new filenames and hycom domains, as well as
        improve graphics -JS & MA 06/2022
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
import numpy as np
import netCDF4 as nc

from datetime import datetime, timedelta

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
  
from pathlib import Path

import pyproj
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeLocator, LongitudeFormatter, LatitudeLocator, LatitudeFormatter)

plt.switch_backend('agg')

#================================================================
model = sys.argv[1]
storm = sys.argv[2]
tcid = sys.argv[3]
cycle = sys.argv[4]
trackon = sys.argv[5]
COMOUT = sys.argv[6]
graphdir = sys.argv[7]

if not os.path.isdir(graphdir):
      p=Path(graphdir)
      p.mkdir(parents=True)

print("code:   MLDnc.py")

cx,cy=coast180()

cx_hycom = np.asarray([cx+360 if cx<74.16 else cx for cx in np.asarray(cx)])
cy_hycom = cy 


if trackon[0].lower()=='y':
   gatcf = glob.glob(COMOUT+'/*.atcfunix')
   if gatcf:
      trackon = 'yes'
   else:
      trackon = 'no'

# Set Cartopy data_dir location (not needed when modulefiles is updated)
#cartopy.config['data_dir'] = '/mnt/lfs4/HFIP/hwrfv3/local/share/cartopy'

#   ------------------------------------------------------------------------------------
# - get SST  *_3z_*.[nc] files
afiles = sorted(glob.glob(os.path.join(COMOUT,'*3z*.nc')))
#afile0 = glob.glob(os.path.join(COMOUT,'*3z.f000.nc'))

#ncfile0 = nc.Dataset(afile0[0])
ncfile0 = xr.open_dataset(afiles[0])

var0 = ncfile0['mixed_layer_thickness']
lon = np.asarray(var0.Longitude)
lat = np.asarray(var0.Latitude)

# define grid boundaries
lonmin = np.min(lon)
lonmax = np.max(lon)
latmin = np.min(lat)
latmax = np.max(lat)
var_name = 'MLD'
units = '(m)'

if np.logical_or(np.min(lon) > 0,np.max(lon) > 360):
    cx = cx_hycom
    cy = cy_hycom

count = len(afiles)        
for k in range(count):

   #ncfile = nc.Dataset(afiles[k])
   ncfile = xr.open_dataset(afiles[k])

   varr = ncfile['mixed_layer_thickness']
   var = np.asarray(varr[0])

   # define forecast hour
   fhr=k*6
   
   # create figure and axes instances
   fig = plt.figure(figsize=(8,4))
   ax = plt.axes(projection=ccrs.PlateCarree())
   ax.axis('scaled')
   
   cflevels = np.linspace(0, 100, 41)
   cmap = plt.get_cmap('RdYlBu_r')
   cf = ax.contourf(lon, lat, var, levels=cflevels, cmap=cmap, extend='both', transform=ccrs.PlateCarree())
   cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=20, shrink=0.6, extendrect=True, ticks=cflevels[::4])
   cb.ax.tick_params(labelsize=8)
   if trackon[0].lower()=='y':
      for m,G in enumerate(gatcf):
         adt,aln,alt,pmn,vmx=readTrack6hrly(G)

         if np.logical_or(np.min(lon) > 0,np.max(lon) > 360):
             aln = np.asarray([ln+360 if ln<74.16 else ln for ln in aln])

         plt.plot(aln,alt,'-ok',markersize=2,alpha=0.4)
         if k < len(aln):
            plt.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None')
   ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

   # Add gridlines and labels
#  gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
   gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
   gl.top_labels = False
   gl.right_labels = False
   gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, 20))
   gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, 10))
   gl.xlabel_style = {'size': 8, 'color': 'black'}
   gl.ylabel_style = {'size': 8, 'color': 'black'}
   
   # Add borders and coastlines
   #ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
   ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
   ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
   ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

   title_center = 'Mixed Layer Depth (m)'
   ax.set_title(title_center, loc='center', y=1.05, fontsize=8)
   title_left = model.upper()+' '+storm.upper()+tcid.upper()
   ax.set_title(title_left, loc='left', fontsize=8)
   title_right = 'Init: '+cycle+'Z '+'F'+"%03d"%(fhr)
   ax.set_title(title_right, loc='right', fontsize=8)
 
   pngFile=os.path.join(graphdir,storm.upper()+tcid.upper()+'.'+cycle+'.'+model.upper()+'.'+var_name+'.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight',dpi=150)
   plt.close("all")

# --- successful exit
sys.exit(0)

