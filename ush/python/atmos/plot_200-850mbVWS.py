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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())
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
uvws=u200-u850
vvws=v200-v850
mag=(uvws**2+vvws**2)**.5

#===================================================================================================
print('Plotting 200-850-hPa for domain1 only')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

mpl.rcParams['figure.figsize'] = [8, 5.4]
fig_name = fig_prefix+'.'+'wind_shear.'+conf['fhhh'].lower()+'.png'
cbshrink = 1.0
skip = round(nlon/360)*10
#skip = round(nlon/360)*20
wblength = 4
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

cflevels = [0,10,20,
            25,30,35,40,
            45,50,55,60,
            65,70,75,80,
            85,90,95,100,105,110,200]  # Maximum value should be 200 so that vws greater than 110kt is light pink 

cfcolors = ['white','white','paleturquoise','darkturquoise','cyan',  
'#3DB388','limegreen','lime','#ADFF2F',
'#FEFE33','#FEED26','#D9C21D','#EDD622',
'#ffc000','#ffa000','#ff8000',
'#F71746','#E21B22','#FF4EA4','#FF93C4','#FFE1FF']

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, mag, cflevels, cmap=cm, norm=norm, transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.01, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=[10,20,30,40,50,60,70,80,90,100,110])
cb.ax.set_yticklabels(['Weak','20\nStrong','30','40','50','60','70','80','90','100','110'])

wb = ax.barbs(lon[::skip,::skip], lat[::skip,::skip], u200[::skip,::skip], v200[::skip,::skip],
              length=wblength, linewidth=0.3, color='purple', transform=transform)
wb = ax.barbs(lon[::skip,::skip], lat[::skip,::skip], u850[::skip,::skip], v850[::skip,::skip],
              length=wblength, linewidth=0.3, color='black', transform=transform)

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
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

title_center = '200-hPa wind (purple), 850-hPa wind (black), and 200-850 hPa VWS (kt, shaded)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
