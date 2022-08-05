#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric MSLP and 10-m wind."""

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
from cartopy.vector_transform import vector_scalar_to_grid
from matplotlib.axes import Axes

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

print('Extracting UGRD, VGRD at 850 mb')
levstr='850 mb'
ugrd = grb.select(shortName='UGRD', level=levstr)[0].data()
ugrd.data[ugrd.mask] = np.nan
ugrd = np.asarray(ugrd) * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data()
vgrd.data[vgrd.mask] = np.nan
vgrd = np.asarray(vgrd) * 1.94384 # convert m/s to kt

# Calculate wind speed
wspd = (ugrd**2+vgrd**2)**.5

#===================================================================================================
print('Plotting 850 hPa STRAMLINE and  Wind Speed ')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 200
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

if conf['stormDomain'] == 'grid02':
    mpl.rcParams['figure.figsize'] = [6, 6]
    fig_name = fig_prefix+'.storm.'+'850mb.streamline.wind.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    skip = 20
    wblength = 4.5
    lonmin = lon[int(nlat/2), int(nlon/2)]-3
    lonmax = lon[int(nlat/2), int(nlon/2)]+3
    latmin = lat[int(nlat/2), int(nlon/2)]-3
    latmax = lat[int(nlat/2), int(nlon/2)]+3
else:
    mpl.rcParams['figure.figsize'] = [8, 5.4]
    fig_name = fig_prefix+'.'+'850mb.streamline.wind.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    skip = round(nlon/360)*10
    wblength = 4
   #skip = 40
    lonmin = np.min(lon)
    lonmax = np.max(lon)
    latmin = np.min(lat)
    latmax = np.max(lat)

myproj = ccrs.PlateCarree()
transform = ccrs.PlateCarree()

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)
ax.coastlines()
cflevels = [0,5,10,15,20,25,30,         # TD
            35,40,45,50,55,60,          # TS
            65,70,75,80,                # H1
            85,90,95,                   # H2
            100,105,110,115,            # H3
            120,125,130,135,            # H4
            140,145,150,155,160,165]    # H5

cfcolors = ['white','white','#e0ffff','#80ffff','#00e0e0','#00c0c0','#00a0a0',                # TD: Cyan
            '#a0ffa0','#00ff00','#00e000','#00c000','#00a000','#008000',                      # TS: Green
            '#ffff80','#e0e000','#c0c000','#a0a000',                                          # H1: Yellow
            '#ffc000','#ffa000','#ff8000',                                                    # H2: Orange
            '#ff8080','#ff6060','#ff4040','#ff0000',                                          # H3: Red
            '#e00000','#c00000','#a00000','#800000',                                          # H4: Darkred
            '#ffa0ff','#ff60ff','#ff00ff','#c000c0','#a000a0','#800080']                      # H5: Magenta
#           '#800080','#a000a0','#c000c0','#ff00ff','#ff60ff','#ffa0ff']                      # H5: Magenta

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, wspd, cflevels, cmap=cm, norm=norm, transform=transform)
#cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
#                  ticks=[10,20,30,35,40,50,60,65,70,80,85,90,100,110,115,120,130,140,150,160])
#cb.ax.set_yticklabels(['10','20','30','TS','40','50','60','H1','70','80','H2','90',
#                       'H3','110','H4','120','130','H5','150','160'])
#cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
#                  ticks=[10,20,30,34,40,50,60,64,70,80,90,96,100,110,120,130,140,150,160])
#cb.ax.set_yticklabels(['10','20','30','TS','40','50','60','HR','70','80','90',
#                       'MH','100','110','120','130','140','150','160'])
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True, 
                  ticks=[10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160])
cb.ax.set_yticklabels(['10','20','30','40','50','60','70','80','90',                       
                       '100','110','120','130','140','150','160'])

#Transform and interpolate a vector field to a regular grid in the target projection
lon_rg, lat_rg, ugrd_rg, vgrd_rg = vector_scalar_to_grid(myproj, myproj,
 (np.shape(lon)[0],np.shape(lon)[1]), lon,lat,ugrd,vgrd)

sb=Axes.streamplot(ax, lon_rg, lat_rg, ugrd_rg, vgrd_rg,linewidth=0.75,density=3, color='black',arrowstyle='->', arrowsize=0.75, transform=transform)
# Add borders and coastlines
#ax.add_feature(cfeature.LAND, facecolor='whitesmoke')
ax.add_feature(cfeature.BORDERS, linewidth=0.5, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.5, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.COASTLINE, linewidth=1.0, facecolor='none', edgecolor='dimgray')

gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.6, color='lightgray', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 8, 'color': 'black'}
gl.ylabel_style = {'size': 8, 'color': 'black'}

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
#ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

title_center = '850-hPa Streamline, Wind Speed (kt,shaded)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
