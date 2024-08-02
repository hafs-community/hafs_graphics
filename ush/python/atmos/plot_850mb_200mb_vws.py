#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric 200-850-hPa Vertical wind shear."""

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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.atm.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())
# The lon range in grib2 is typically between 0 and 360
# Cartopy's PlateCarree projection typically uses the lon range of -180 to 180
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
if abs(np.max(lon) - 360.) < 10.:
    lon[lon>180] = lon[lon>180] - 360.
    lon_offset = 0.
else:
    lon_offset = 180.
lon = lon - lon_offset
print('new lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
[nlat, nlon] = np.shape(lon)

#==========================================================
print('Extracting UGRD, VGRD at 200 hPa')
levstr='200 mb'
u200 = grb.select(shortName='UGRD', level=levstr)[0].data()
u200.data[u200.mask] = np.nan
u200 = np.asarray(u200) * 1.94384 # convert m/s to kt

v200 = grb.select(shortName='VGRD', level=levstr)[0].data()
v200.data[v200.mask] = np.nan
v200 = np.asarray(v200) * 1.94384 # convert m/s to kt

#==========================================================
print('Extracting UGRD, VGRD at 850 hPa')
levstr='850 mb'
u850 = grb.select(shortName='UGRD', level=levstr)[0].data()
u850.data[u850.mask] = np.nan
u850 = np.asarray(u850) * 1.94384 # convert m/s to kt

v850 = grb.select(shortName='VGRD', level=levstr)[0].data()
v850.data[v850.mask] = np.nan
v850 = np.asarray(v850) * 1.94384 # convert m/s to kt

# Calculate VWS
uvws = u200-u850
vvws = v200-v850
mag = (uvws**2+vvws**2)**.5

#===================================================================================================
print('Plotting 200-850-hPa vertical wind shear')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 8
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

if conf['stormDomain'] == 'storm':
    mpl.rcParams['figure.figsize'] = [6, 6]
    fig_name = fig_prefix+'.storm.'+'850mb_200mb_vws.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    lonmin = lon[int(nlat/2), int(nlon/2)]-3
    lonmax = lon[int(nlat/2), int(nlon/2)]+3
    lonint = 2.0
    latmin = lat[int(nlat/2), int(nlon/2)]-3
    latmax = lat[int(nlat/2), int(nlon/2)]+3
    latint = 2.0
    skip = 20
    wblength = 4.5
else:
    mpl.rcParams['figure.figsize'] = [8, 5.4]
    fig_name = fig_prefix+'.'+'850mb_200mb_vws.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    lonmin = np.min(lon)
    lonmax = np.max(lon)
    lonint = 10.0
    latmin = np.min(lat)
    latmax = np.max(lat)
    latint = 10.0
    skip = round(nlon/360)*10
    wblength = 4
   #skip = 40

myproj = ccrs.PlateCarree(lon_offset)
transform = ccrs.PlateCarree(lon_offset)

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

cflevels = [0,5,10,15,
            20,25,30,35,
            40,45,50,
            55,60,65,70,
            75,80,85,90,
            95,100,105,110,115,120]

cfcolors = ['#ffffff','#80ffff','#00c0c0','#00a0a0', # Cyan
            '#ffff80','#e0e000','#c0c000','#a0a000', # Yellow
            '#ffc000','#ffa000','#ff8000',           # Orange
            '#ff8080','#ff6060','#ff4040','#ff0000', # Red
            '#e00000','#c00000','#a00000','#800000', # Darkred
            '#800080','#a000a0','#c000c0','#ff00ff','#ff60ff','#ffa0ff'] # Magenta
#           '#ffa0ff','#ff60ff','#ff00ff','#c000c0','#a000a0','#800080'] # Magenta

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, mag, cflevels, cmap=cm, norm=norm, extend='max', transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.01, aspect=50, extend='max', shrink=cbshrink, extendrect=True,
                  ticks=cflevels[::2])

lat_nh = lat[lat[:,0]>=0,:] 
lon_nh = lon[lat[:,0]>=0,:] 
u200_nh = u200[lat[:,0]>=0,:] 
v200_nh = v200[lat[:,0]>=0,:] 
u850_nh = u850[lat[:,0]>=0,:] 
v850_nh = v850[lat[:,0]>=0,:] 

lat_sh = lat[lat[:,0]<0,:] 
lon_sh = lon[lat[:,0]<0,:] 
u200_sh = u200[lat[:,0]<0,:] 
v200_sh = v200[lat[:,0]<0,:] 
u850_sh = u850[lat[:,0]<0,:] 
v850_sh = v850[lat[:,0]<0,:] 

wb1 = ax.barbs(lon_nh[::skip,::skip], lat_nh[::skip,::skip], u200_nh[::skip,::skip], v200_nh[::skip,::skip],
               length=wblength, linewidth=0.3, color='blue', transform=transform,flip_barb=False)
wb1 = ax.barbs(lon_sh[::skip,::skip], lat_sh[::skip,::skip], u200_sh[::skip,::skip], v200_sh[::skip,::skip],
               length=wblength, linewidth=0.3, color='blue', transform=transform,flip_barb=True)

wb2 = ax.barbs(lon_nh[::skip,::skip], lat_nh[::skip,::skip], u850_nh[::skip,::skip], v850_nh[::skip,::skip],
               length=wblength, linewidth=0.3, color='black', transform=transform,flip_barb=False)
wb2 = ax.barbs(lon_sh[::skip,::skip], lat_sh[::skip,::skip], u850_sh[::skip,::skip], v850_sh[::skip,::skip],
               length=wblength, linewidth=0.3, color='black', transform=transform,flip_barb=True)

# Add borders and coastlines
#ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

#gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, lonint))
gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, latint))
gl.xlabel_style = {'size': 8, 'color': 'black'}
gl.ylabel_style = {'size': 8, 'color': 'black'}

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

model_info = os.environ.get('TITLEgraph','').strip()
var_info = '200 hPa Wind (blue), 850 hPa Wind (black), 200-850 hPa VWS (kt, shaded)'
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}
{1}
{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_left, loc='left', y=0.99)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax.text(1.0,-0.04, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
