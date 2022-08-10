#!/usr/bin/env python3

"""This script plots out HAFS the 3-hours accumulated precipitation, the mean sea level pressure and the 1000-500 geopotential thickness."""

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

if conf['stormDomain'] == 'grid01':
    grb_apcp = grb # extract apcp from domain grid01

if conf['stormDomain'] == 'grid02':
    fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+'grid01'+'.'+conf['fhhh']+'.grb2'
    grib2file = os.path.join(conf['COMhafs'], fname)
    print(f'grib2file for accumulated precipitation: {grib2file}')
    grb_apcp = grib2io.open(grib2file,mode='r') # extract apcp from domain grid01

    print('Extracting lat, lon for accumulated precipitation')
    lat_apcp = np.asarray(grb_apcp.select(shortName='NLAT')[0].data())
    lon_apcp = np.asarray(grb_apcp.select(shortName='ELON')[0].data())
    #[nlat, nlon] = np.shape(lon)

print('Extracting lat, lon')
lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())
[nlat, nlon] = np.shape(lon)

print('Extracting PRMSL')
slp = grb.select(shortName='PRMSL',level='mean sea level')[0].data()
slp.data[slp.mask] = np.nan
slp = np.asarray(slp) * 0.01 # convert Pa to hPa
slp = gaussian_filter(slp, 2)

print('Extracting accumulate precipitation at surface')
levstr='surface'
apcp = grb_apcp.select(shortName='APCP', level=levstr)[0].data()*0.0393701  # convert kg/m^2 to in
apcp.data[apcp.mask] = np.nan
apcp = gaussian_filter(apcp, 2)

print('Extracting height of the 1000 mb geopotential ')
levstr='1000 mb'
hgt1000 = grb.select(shortName='HGT', level=levstr)[0].data()
hgt1000.data[hgt1000.mask] = np.nan

print('Extracting height of the 500 mb geopotential ')
levstr='500 mb'
hgt500 = grb.select(shortName='HGT', level=levstr)[0].data()
hgt500.data[hgt500.mask] = np.nan

print('Calculating the 1000-500 geopotential thickness ')
thk1000_500 = (hgt500 - hgt1000)/10
thk1000_500 = gaussian_filter(thk1000_500, 2)

#===================================================================================================
print('Plotting MSLP, APCP and 1000-500 geopotential thickness ')
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
    fig_name = fig_prefix+'.storm.'+'precip_mslp_thk.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
    lonmin = lon[int(nlat/2), int(nlon/2)]-3
    lonmax = lon[int(nlat/2), int(nlon/2)]+3
    latmin = lat[int(nlat/2), int(nlon/2)]-3
    latmax = lat[int(nlat/2), int(nlon/2)]+3
else:
    mpl.rcParams['figure.figsize'] = [8, 5.4]
    fig_name = fig_prefix+'.'+'precip_mslp_thk.'+conf['fhhh'].lower()+'.png'
    cbshrink = 1.0
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

cslevels = np.arange(900,1050,4)
cs = ax.contour(lon, lat,slp, levels=cslevels, colors='black', linewidths=0.6, transform=transform)
lblevels = np.arange(900,1050,8)
lb = plt.clabel(cs, levels=lblevels, inline_spacing=1, fmt='%d', fontsize=6)

cslevels = np.arange(540,600,4)
cs = ax.contour(lon, lat,thk1000_500, levels=cslevels, colors='red', linewidths=0.6, transform=transform)
lblevels = np.arange(540,600,8)
lb = plt.clabel(cs, levels=lblevels, inline_spacing=1, fmt='%d', fontsize=6)

cflevels = [0,                   # white
            0.01,0.1,0.25,       # blue
            0.5,0.75,1,          # green
            1.5,2,2.5,           # yellow
            3,4,5,               # red
            6,8,10,11]           # purple

cfcolors = ['white',                                       # white
            'deepskyblue','cornflowerblue','mediumblue',   # blue
            'lawngreen','mediumseagreen', 'green',         # green
            'yellow','gold','orange',                      # yellow
            'orangered','indianred','firebrick',           # red
            'mediumvioletred','darkorchid','darkmagenta']  # purple

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

if conf['stormDomain'] == 'grid01':
    cf = ax.contourf(lon, lat, apcp, cflevels, cmap=cm, norm=norm, transform=transform)
elif conf['stormDomain'] == 'grid02':
    cf = ax.contourf(lon_apcp, lat_apcp, apcp, cflevels, cmap=cm, norm=norm, transform=transform)

cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=[0.01,0.1,0.25,0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10])
cb.ax.set_yticklabels(['0.01','0.1','0.25','0.5','0.75','1','1.5','2.0','2.5','3.0','4.0','5.0','6.0','8.0','10.0'])

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

title_center = '3 h Acc. Precip. (in, shaded), MSLP (hPa), 1000-500 hPa Thickness (dam, red)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
