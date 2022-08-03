#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric vorticity, geopotential height,
and wind figures on standard layers (e.g., 850, 700, 500, 300, 200 hPa)."""

import os
import sys
import logging
import math
import datetime

import yaml
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

import grib2io
from netCDF4 import Dataset

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable

import pyproj
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import (LongitudeLocator, LongitudeFormatter, LatitudeLocator, LatitudeFormatter)

# Parse the yaml config file
print('Parse the config file: plot_atmos.yml:')
with open('plot_atmos.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')   

print('Extracting lat, lon')
lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())
[nlat, nlon] = np.shape(lon)

RHlevs=np.arange(500,701,25)
print(RHlevs)
for ind, lv in enumerate(RHlevs):
  levstr= str(lv)+' mb'
  print('Extracting RH at '+levstr)
  rh = grb.select(shortName='RH', level=levstr)[0].data()
  rh.data[rh.mask] = np.nan
  rh[rh<0.] = np.nan
  rh = np.asarray(rh)
  if ind == 0:
    rhtmp=np.zeros((len(RHlevs),rh.shape[0],rh.shape[1]))
    print(rhtmp.shape)
    rhtmp[ind,:,:]=rh
  rhtmp[ind,:,:]=rh
print(rhtmp.shape)

rhave = np.mean(rhtmp,axis=0)
print(rhave.shape)

levstr=str(conf['standardLayer'])+' mb'
print('Extracting HGT, UGRD, VGRD, at '+levstr)
hgt = grb.select(shortName='HGT', level=levstr)[0].data()
hgt.data[hgt.mask] = np.nan
hgt = np.asarray(hgt) * 0.1 # convert meter to decameter
hgt = gaussian_filter(hgt, 5)

ugrd = grb.select(shortName='UGRD', level=levstr)[0].data()
ugrd.data[ugrd.mask] = np.nan
ugrd = np.asarray(ugrd) * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data()
vgrd.data[vgrd.mask] = np.nan
vgrd = np.asarray(vgrd) * 1.94384 # convert m/s to kt
    
    #===================================================================================================
print('Plotting HGT, RH, UGRD, VGRD, at '+levstr)
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 200 #150
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8
    
if conf['stormDomain'] == 'grid02':
  mpl.rcParams['figure.figsize'] = [6, 6]
  fig_name = fig_prefix+'.storm.'+str(conf['standardLayer'])+'mb.rh.hgt.wind.'+conf['fhhh'].lower()+'.png'
  cbshrink = 1.0
  lonmin = lon[int(nlat/2), int(nlon/2)]-3
  lonmax = lon[int(nlat/2), int(nlon/2)]+3
  latmin = lat[int(nlat/2), int(nlon/2)]-3
  latmax = lat[int(nlat/2), int(nlon/2)]+3
  skip = 20
  wblength = 4.5
  barbcol = 'black'
  hgtcol = 'black'
else:
  mpl.rcParams['figure.figsize'] = [8, 4.8]
  fig_name = fig_prefix+'.'+str(conf['standardLayer'])+'mb.rh.hgt.wind.'+conf['fhhh'].lower()+'.png'
  cbshrink = 1.0
  lonmin = np.min(lon)
  lonmax = np.max(lon)
  latmin = np.min(lat)
  latmax = np.max(lat)
  skip = round(nlon/360)*10
  wblength = 4
  barbcol = 'black'
  hgtcol = 'black'
    
if conf['standardLayer'] == 200:
    cslevels=np.arange(1080,1290,12)
elif conf['standardLayer'] == 300:
    cslevels=np.arange(780,1020,12)
elif conf['standardLayer'] == 500:
    cslevels=np.arange(480,600,6)
elif conf['standardLayer'] == 700:
    cslevels=np.arange(210,330,3)
elif conf['standardLayer'] == 850:
    cslevels=np.arange(60,180,3)
else:
    cslevels=np.arange(-50,4000,5)
    
myproj = ccrs.PlateCarree()
transform = ccrs.PlateCarree()

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

cflevels = np.arange(10,91,5)

cf = ax.contourf(lon, lat, rhave, levels=cflevels, cmap=plt.cm.get_cmap('BrBG') ,extend='both')
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, extend='both', extendfrac='auto', shrink=cbshrink, extendrect=True, ticks=cflevels)

wb = ax.barbs(lon[::skip,::skip], lat[::skip,::skip], ugrd[::skip,::skip], vgrd[::skip,::skip], 
              length=wblength, linewidth=0.2, color=barbcol, transform=transform)

cs = ax.contour(lon, lat, hgt, levels=cslevels, colors=hgtcol, linewidths=0.9, transform=transform)
lb = plt.clabel(cs, levels=cslevels, inline_spacing=1, fmt='%d', fontsize=8)

# Add borders and coastlines
ax.add_feature(cfeature.BORDERS, linewidth=0.8, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.8, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.COASTLINE, linewidth=1.4, facecolor='none', edgecolor='dimgray')

gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.6, color='lightgray', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 12, 'color': 'black'}
gl.ylabel_style = {'size': 12, 'color': 'black'}

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

        
title_center = '700-500 hPa mean RH (shaded, %),'+ '700 hPa Height (dam), 700 hPa Wind (kt)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')
  
#plt.show() 
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
