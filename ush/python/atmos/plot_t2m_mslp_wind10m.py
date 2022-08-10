#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric surface temperature, MSLP and 10-m wind."""

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

print('Extracting Temperature at 2 m above ground')
levstr='2 m above ground'
tmp = grb.select(shortName='TMP', level=levstr)[0].data()
tmp.data[tmp.mask] = np.nan
tmp = np.asarray(tmp) - 273.15 # convert K to degC
tmp = gaussian_filter(tmp, 2)

print('Extracting PRMSL')
slp = grb.select(shortName='PRMSL',level='mean sea level')[0].data()
slp.data[slp.mask] = np.nan
slp = np.asarray(slp) * 0.01 # convert Pa to hPa
slp = gaussian_filter(slp, 5)

print('Extracting UGRD, VGRD at 10 m above ground')
levstr='10 m above ground'
ugrd = grb.select(shortName='UGRD', level=levstr)[0].data()
ugrd.data[ugrd.mask] = np.nan
ugrd = np.asarray(ugrd) * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data()
vgrd.data[vgrd.mask] = np.nan
vgrd = np.asarray(vgrd) * 1.94384 # convert m/s to kt

# Calculate wind speed
wspd = (ugrd**2+vgrd**2)**.5

#===================================================================================================
print('Plotting 2 m temperature, MSLP and 10 m wind')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

if conf['stormDomain'] == 'grid02':
    mpl.rcParams['figure.figsize'] = [6, 6]
    fig_name = fig_prefix+'.storm.'+'t2m_mslp_wind10m.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    lonmin = lon[int(nlat/2), int(nlon/2)]-3
    lonmax = lon[int(nlat/2), int(nlon/2)]+3
    latmin = lat[int(nlat/2), int(nlon/2)]-3
    latmax = lat[int(nlat/2), int(nlon/2)]+3
    skip = 20
    wblength = 4.5
else:
    mpl.rcParams['figure.figsize'] = [8, 5.4]
    fig_name = fig_prefix+'.'+'t2m_mslp_wind10m.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    lonmin = np.min(lon)
    lonmax = np.max(lon)
    latmin = np.min(lat)
    latmax = np.max(lat)
    skip = round(nlon/360)*10
    wblength = 4
   #skip = 40


myproj = ccrs.PlateCarree()
transform = ccrs.PlateCarree()

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

cflevels = np.linspace(-20, 40, 121)
ctmp = plt.get_cmap('nipy_spectral')
cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name,ctmp(np.linspace(0.04, 0.98, 201)))
cf = ax.contourf(lon, lat, tmp, levels=cflevels, cmap=cmap, extend='both', transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True, ticks=cflevels[::10])

wb = ax.barbs(lon[::skip,::skip], lat[::skip,::skip], ugrd[::skip,::skip], vgrd[::skip,::skip],
              length=wblength, linewidth=0.2, color='black', transform=transform)

cslevels = np.arange(840,1040,4)
cs = ax.contour(lon, lat, slp, levels=cslevels, colors='black', linewidths=0.6, transform=transform)
lblevels = np.arange(840,1040,8)
lb = plt.clabel(cs, levels=lblevels, inline_spacing=1, fmt='%d', fontsize=8)

# Add borders and coastlines
#ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 8, 'color': 'black'}
gl.ylabel_style = {'size': 8, 'color': 'black'}

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

title_center = '2 m Temperature (${^o}$C, shaded), MSLP (hPa), 10 m Wind (kt)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
