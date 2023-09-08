"""

 plot_z20.py
 -------------
    read a HYCOM 3z .nc file,
    extract Z20 and plot in time series.


 ************************************************************************
 usage: python plot_z20.py stormModel stormName stormID YMDH trackon COMhafs graphdir
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

import os
import sys
import glob
import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
  
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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

print("code:   plot_z20.py")

if trackon[0].lower()=='y':
   atcf = COMOUT+'/' + tcid + '.' + cycle + '.' + model + '.trak.atcfunix'
   if atcf:
      trackon = 'yes'
   else:
      trackon = 'no'

# Set Cartopy data_dir location
cartopy.config['data_dir'] = os.getenv('cartopyDataDir')

#   ------------------------------------------------------------------------------------
# - get SST  *_3z_*.[nc] files
afiles = sorted(glob.glob(os.path.join(COMOUT,tcid+'*3z*.nc')))

ncfile0 = xr.open_dataset(afiles[0])

temp = ncfile0['temperature'].isel(Z=0)
var0 = ncfile0['depth of 20C isotherm']
lon = np.asarray(ncfile0.Longitude)
lat = np.asarray(ncfile0.Latitude)
lonmin_raw = np.min(lon)
lonmax_raw = np.max(lon)
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

# Constrain lon limits between -180 and 180 so it does not conflict with the cartopy projection PlateCarree
lon[lon>180] = lon[lon>180] - 360
sort_lon = np.argsort(lon)
lon = lon[sort_lon]

# define grid boundaries
lonmin = np.min(lon)
lonmax = np.max(lon)
latmin = np.min(lat)
latmax = np.max(lat)
print('new lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

var_name = 'z20'
units = '(m)'

# Shift central longitude so the Southern Hemisphere and North Indin Ocean domains are plotted continuously
if np.logical_and(lonmax >= 90, lonmax <=180):
    central_longitude = 90
else:
    central_longitude = -90
print('central longitude: ',central_longitude)

# reduce array size to 2D
temp = np.squeeze(temp)
var0 = np.squeeze(var0)

# reshape arrays to 1D for boolean indexing
ind = temp.shape
temp = np.reshape(np.asarray(temp),(ind[0]*ind[1],1))
var0 = np.reshape(np.asarray(var0),(ind[0]*ind[1],1))
var0[np.argwhere(np.isnan(temp))] = np.nan
var0 = np.reshape(var0,(ind[0],ind[1]))

count = len(afiles)        
for k in range(count):

   ncfile = xr.open_dataset(afiles[k])
   varr = ncfile['depth of 20C isotherm']
   var = np.asarray(varr[0])

   # land mask
   var = np.reshape(np.asarray(var),(ind[0]*ind[1],1))
   var[np.argwhere(np.isnan(temp))] = np.nan
   var = np.reshape(var,(ind[0],ind[1]))
   # sort var according to the new longitude
   var = var[:,sort_lon]

   # define forecast hour
   fhr=k*6
   
   # create figure and axes instances
   fig = plt.figure(figsize=(8,4))
   ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=central_longitude))
   ax.axis('scaled')
   
   cflevels = np.linspace(0, 300, 61)
   cmap = plt.get_cmap('RdYlBu_r')
   cf = ax.contourf(lon, lat, var, levels=cflevels, cmap=cmap, extend='max', transform=ccrs.PlateCarree())
   cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=20, shrink=0.6, extendrect=True, ticks=cflevels[::10])
   cb.ax.tick_params(labelsize=8)

   if trackon[0].lower()=='y':
       adt,aln,alt,pmn,vmx=readTrack6hrly(atcf)
       aln[np.logical_or(aln<lonmin,aln>lonmax)] = np.nan
       ax.plot(aln,alt,'-ok',markersize=2,alpha=0.4,transform=ccrs.PlateCarree(central_longitude=0))
       if k < len(aln):
           ax.plot(aln[k],alt[k],'ok',markersize=6,alpha=0.4,markerfacecolor='None',transform=ccrs.PlateCarree(central_longitude=0))

   ax.set_extent([lonmin_raw, lonmax_raw, latmin, latmax], crs=ccrs.PlateCarree())

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

   model_info = os.environ.get('TITLEgraph','').strip()
   var_info = 'Depth of 20${^o}$C Isotherm (m)'
   storm_info = storm.upper()+tcid.upper()
   title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
   ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
   title_right = 'Init: '+cycle+'Z '+'F'+"%03d"%(fhr)
   ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
   footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
   ax.text(1.0,-0.1, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

   pngFile=os.path.join(graphdir,storm.upper()+tcid.upper()+'.'+cycle+'.'+model.upper()+'.ocean.'+var_name+'.f'+"%03d"%(fhr)+'.png')
   plt.savefig(pngFile,bbox_inches='tight',dpi=150)
   plt.close("all")

# --- successful exit
sys.exit(0)

