#!/usr/bin/env python3

"""This script is to plot out HAFS simulated SSMIS F17 microwave 37GHz brightness temperature."""

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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.sat.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting SSMS1715 grid information')
grb_grid = grb.select(shortName='SSMS1715')[0].gridDefinitionTemplate
nlon = grb_grid[7]
nlat = grb_grid[8]
blat = grb_grid[11]/1.e6
blon = grb_grid[12]/1.e6
elat = grb_grid[14]/1.e6
elon = grb_grid[15]/1.e6
dlat = grb_grid[16]/1.e6
dlon = grb_grid[17]/1.e6
lat1d = np.linspace(blat, elat, nlat)
if elon > blon:
    lon1d = np.linspace(blon, elon, nlon)
else:
    lon1d = np.linspace(blon, 360.+elon, nlon)
    lon1d = np.mod(lon1d, 360.)

[lon, lat] = np.meshgrid(lon1d, lat1d)

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
#[nlat, nlon] = np.shape(lon)

print('Extracting SSMS1715')
mw = grb.select(shortName='SSMS1715')[0].data()
mw.data[mw.mask] = np.nan
#mw = np.asarray(mw)-273.15 # convert K to deg C
mw = gaussian_filter(mw, 2)

#===================================================================================================
print('Plotting SSMS1715')
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
    fig_name = fig_prefix+'.storm.'+'ssmisf17_mw37ghz.'+conf['fhhh'].lower()+'.png'
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
    fig_name = fig_prefix+'.'+'ssmisf17_mw37ghz.'+conf['fhhh'].lower()+'.png'
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

cflevels = [150,150.6933,151.3866,152.0798,152.7731,153.4664,154.1597,154.8529,155.5462,156.2395,156.9328,157.6261,158.3193,159.0126,159.7059,160.3992,161.0924,161.7857,162.479,163.1723,163.8655,164.5588,165.2521,165.9454,166.6387,167.3319,168.0252,168.7185,169.4118,170.105,170.7983,171.4916,172.1849,172.8782,173.5714,174.2647,174.958,175.6513,176.3445,177.0378,177.7311,178.4244,179.1176,179.8109,180.5042,181.1975,181.8908,182.584,183.2773,183.9706,184.6639,185.3571,186.0504,186.7437,187.437,188.1303,188.8235,189.5168,190.2101,190.9034,191.5966,192.2899,192.9832,193.6765,194.3697,195.063,195.7563,196.4496,197.1429,197.8361,198.5294,199.2227,199.916,200.6092,201.3025,201.9958,202.6891,203.3824,204.0756,204.7689,205.4622,206.1555,206.8487,207.542,208.2353,208.9286,209.6218,210.3151,211.0084,211.7017,212.395,213.0882,213.7815,214.4748,215.1681,215.8613,216.5546,217.2479,217.9412,218.6345,219.3277,220.021,220.7143,221.4076,222.1008,222.7941,223.4874,224.1807,224.8739,225.5672,226.2605,226.9538,227.6471,228.3403,229.0336,229.7269,230.4202,231.1134,231.8067,232.5,233.1933,233.8866,234.5798,235.2731,235.9664,236.6597,237.3529,238.0462,238.7395,239.4328,240.1261,240.8193,241.5126,242.2059,242.8992,243.5924,244.2857,244.979,245.6723,246.3655,247.0588,247.7521,248.4454,249.1387,249.8319,250.5252,251.2185,251.9118,252.605,253.2983,253.9916,254.6849,255.3782,256.0714,256.7647,257.458,258.1513,258.8445,259.5378,260.2311,260.9244,261.6176,262.3109,263.0042,263.6975,264.3908,265.084,265.7773,266.4706,267.1639,267.8571,268.5504,269.2437,269.937,270.6303,271.3235,272.0168,272.7101,273.4034,274.0966,274.7899,275.4832,276.1765,276.8697,277.563,278.2563,278.9496,279.6429,280.3361,281.0294,281.7227,282.416,283.1092,283.8025,284.4958,285.1891,285.8824,286.5756,287.2689,287.9622,288.6555,289.3487,290.042,290.7353,291.4286,292.1218,292.8151,293.5084,294.2017,294.895,295.5882,296.2815,296.9748,297.6681,298.3613,299.0546,299.7479,300.4412,301.1345,301.8277,302.521,303.2143,303.9076,304.6008,305.2941,305.9874,306.6807,307.3739,308.0672,308.7605,309.4538,310.1471,310.8403,311.5336,312.2269,312.9202,313.6134,314.3067,315]

cfcolors = [(124,4,131),(120,8,135),(117,11,138),(113,15,142),(110,18,145),(106,22,149),(103,25,152),(99,29,156),(95,33,160),(92,36,163),(88,40,167),(84,44,171),(81,47,174),(77,51,178),(74,54,181),(70,58,185),(66,62,189),(62,65,193),(59,69,196),(55,73,200),(51,76,204),(48,80,207),(44,83,211),(41,87,214),(37,90,217),(33,94,222),(30,98,225),(26,101,228),(22,105,233),(19,109,236),(16,112,239),(12,116,243),(8,119,246),(5,123,250),(1,127,254),(3,130,255),(6,133,255),(10,137,255),(14,141,255),(17,144,255),(21,148,255),(24,151,255),(28,155,255),(32,159,255),(35,162,255),(39,166,255),(43,170,255),(46,173,255),(49,176,255),(53,180,255),(57,184,255),(60,187,255),(64,192,255),(68,195,255),(71,198,255),(75,203,255),(79,206,255),(82,209,255),(86,213,255),(89,216,255),(93,220,255),(96,224,255),(100,227,255),(104,231,255),(107,235,255),(111,238,255),(114,242,255),(118,245,255),(122,249,255),(125,253,255),(128,255,253),(128,255,245),(128,255,238),(128,255,231),(128,255,224),(128,255,216),(128,255,209),(128,255,202),(128,255,195),(128,255,188),(128,255,180),(128,255,173),(128,255,166),(128,255,159),(128,255,152),(128,255,144),(128,255,137),(128,255,130),(132,255,128),(140,255,128),(147,255,128),(154,255,128),(161,255,128),(168,255,128),(176,255,128),(183,255,128),(190,255,128),(197,255,128),(205,255,128),(212,255,128),(219,255,128),(226,255,128),(233,255,128),(241,255,128),(248,255,128),(255,255,128),(255,251,124),(255,247,120),(255,244,117),(255,240,113),(255,237,110),(255,233,106),(255,230,103),(255,226,99),(255,222,95),(255,219,92),(255,215,88),(255,211,84),(255,208,81),(255,204,77),(255,201,74),(255,197,70),(255,193,66),(255,190,62),(255,186,59),(255,182,55),(255,179,51),(255,175,48),(255,172,44),(255,168,41),(255,165,37),(255,161,33),(255,157,30),(255,154,26),(255,150,22),(255,146,19),(255,143,15),(255,139,12),(255,136,8),(255,132,5),(255,129,1),(252,125,0),(249,122,0),(245,118,0),(241,114,0),(238,111,0),(234,107,0),(231,104,0),(227,100,0),(223,96,0),(220,93,0),(216,89,0),(212,85,0),(209,82,0),(206,79,0),(202,75,0),(198,71,0),(195,68,0),(191,63,0),(187,60,0),(184,56,0),(180,52,0),(176,49,0),(173,46,0),(169,42,0),(166,38,0),(162,35,0),(158,31,0),(155,27,0),(151,24,0),(147,20,0),(144,16,0),(141,13,0),(137,9,0),(133,6,0),(130,2,0),(127,2,0),(125,9,0),(122,16,0),(120,22,0),(117,29,0),(114,36,0),(112,42,0),(109,49,0),(107,56,0),(104,63,0),(102,69,0),(99,76,0),(97,83,0),(94,89,0),(92,96,0),(89,103,0),(87,109,0),(84,116,0),(82,123,0),(79,129,0),(77,136,0),(74,143,0),(72,150,0),(69,156,0),(66,163,0),(64,170,0),(61,176,0),(59,183,0),(56,190,0),(54,196,0),(51,203,0),(52,197,3),(52,189,7),(53,182,10),(54,174,14),(54,166,17),(55,158,21),(56,150,24),(56,142,28),(57,135,31),(58,127,35),(58,119,38),(59,111,42),(60,103,45),(60,95,49),(61,88,52),(62,80,55),(62,72,59),(63,64,62),(75,75,75),(89,89,89),(103,103,103),(116,116,116),(130,130,130),(144,144,144),(158,158,158),(172,172,172),(186,186,186),(200,200,200),(213,213,213),(227,227,227),(241,241,241),(255,255,255)]

cfcolors = np.divide(cfcolors, 255.)

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, mw, cflevels, cmap=cm, extend='both', norm=norm, transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=np.linspace(150.,310.,17))

# Add borders and coastlines
#ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
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

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

title_center = 'Simulated SSMIS F17 H 37 GHz Microwave Brightness Temperature (K)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
