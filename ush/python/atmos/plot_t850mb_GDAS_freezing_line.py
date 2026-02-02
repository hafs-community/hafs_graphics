#!/usr/bin/env python3

"""This script is to plot out GDAS 850 mbar temperature and freezing line."""

import os

import yaml
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

import grib2io

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Parse the yaml config file
print('Parse the config file: plot_atmos.yml:')
with open('plot_atmos.yml', 'rt') as f:
    conf = yaml.safe_load(f)
#conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

# GDAS
gdas_time = conf['validTime']
gdas_year = str(gdas_time.year)
gdas_month = [str(gdas_time.month) if len(str(gdas_time.month)) > 1 else '0'+str(gdas_time.month)][0]
gdas_day = [str(gdas_time.day) if len(str(gdas_time.day)) > 1 else '0'+str(gdas_time.day)][0]
gdas_hour = [str(gdas_time.hour) if len(str(gdas_time.hour)) > 1 else '0'+str(gdas_time.hour)][0]
gdas_cycle = gdas_year + gdas_month + gdas_day + gdas_hour

gdasdir = conf['gdasdir']
gdasfile = gdasdir + 'pgbanl.gdas.' + gdas_cycle
print(f'gdasfile: {gdasfile}')
gdas = grib2io.open(gdasfile,mode='r')

print('Extracting Temperature at 850 mb')
levstr='850 mb'
tmp_gdas = gdas.select(shortName='TMP', level=levstr)[0].data
tmp_gdas = tmp_gdas - 273.15 # convert K to degC
#tmp = gaussian_filter(tmp, 2)

print('Extracting lat, lon')
record = gdas.select(shortName='TMP')[0]
lat, lon = record.latlons()

lon_offset = 0.
[nlat, nlon] = np.shape(lon)

#===================================================================================================
print('Plotting 850 mbar temperature')
fig_prefix = conf['model']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 8
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

mpl.rcParams['figure.figsize'] = [8, 5.4]
fig_name = fig_prefix+'.'+'t850mb_gdas.'+conf['ymdh']+'.png'
cbshrink = 0.7
lonmin = conf['lonmin']
lonmax = conf['lonmax']
lonint = 10.0
latmin = conf['latmin']
latmax = conf['latmax']
latint = 10.0
skip = round(nlon/360)*10
wblength = 4

myproj = ccrs.PlateCarree(lon_offset)
transform = ccrs.PlateCarree(lon_offset)

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('scaled')

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

#cflevels = np.linspace(-20, 40, 121)
cflevels = np.linspace(-20, 40, 61)
ctmp = plt.get_cmap('nipy_spectral')
cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name,ctmp(np.linspace(0.04, 0.98, 201)))
cf = ax.contourf(lon, lat, tmp_gdas, levels=cflevels, cmap=cmap, extend='both')
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, shrink=cbshrink, extendrect=True, ticks=cflevels[::10])

ax.contour(lon, lat, tmp_gdas, levels=[0], colors='black', linewidths=2)
plt.plot([0], [0], color='black', lw=2, label='GDAS')
plt.legend(loc='lower right')

# Add borders and coastlines
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, lonint))
gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, latint))
gl.xlabel_style = {'size': 8, 'color': 'black'}
gl.ylabel_style = {'size': 8, 'color': 'black'}

model_info = conf['model']
var_info = '850 mbar Temperature (${^o}$C, shaded), Freezing Line (solid line)'
storm_info = " "
title_center = """{0} {1}
{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_center, loc='center', y=0.99)
title_right = conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99)

plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
