#!/usr/bin/env python3

"""This script is to plot out ARAFS atmospheric surface temperature, MSLP and 10-m wind."""

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
print('Parse the config file: plot_atmos_diff.yml:')
with open('plot_atmos_diff.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

grib2dir_ctl = conf['grib2dir_ctl']
grib2file_ctl = grib2dir_ctl + 'pgb' + conf['fhhh'] + '.' + conf['ymdh']
print(f'grib2file_ctl: {grib2file_ctl}')
grb_ctl = grib2io.open(grib2file_ctl,mode='r')

grib2dir_deny = conf['grib2dir_deny']
grib2file_deny = grib2dir_deny + 'pgb' + conf['fhhh'] + '.' + conf['ymdh']
print(f'grib2file_deny: {grib2file_deny}')
grb_deny = grib2io.open(grib2file_deny,mode='r')

print('Extracting lat, lon')
record_ctl = grb_ctl.select(shortName='TMP')[0]
lat, lon = record_ctl.latlons()

'''
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
if abs(np.max(lon) - 360.) < 10.:
    lon[lon>180] = lon[lon>180] - 360.
    lon_offset = 0.
else:
    lon_offset = 180.
lon = lon - lon_offset
print('new lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
'''
lon_offset = 0.
[nlat, nlon] = np.shape(lon)

print('Extracting Temperature at 2 m above ground')
levstr='2 m above ground'
tmp_ctl = grb_ctl.select(shortName='TMP', level=levstr)[0].data
tmp_ctl = tmp_ctl - 273.15 # convert K to degC
tmp_ctl = gaussian_filter(tmp_ctl, 2)
tmp_deny = grb_deny.select(shortName='TMP', level=levstr)[0].data
tmp_deny = tmp_deny - 273.15 # convert K to degC
tmp_deny = gaussian_filter(tmp_deny, 2)

print('Extracting MSLET')
slp_ctl = grb_ctl.select(shortName='MSLET')[0].data
slp_ctl = slp_ctl * 0.01 # convert Pa to hPa
slp_deny = grb_deny.select(shortName='MSLET')[0].data
slp_deny = slp_deny * 0.01 # convert Pa to hPa

'''
print('Extracting UGRD, VGRD at 10 m above ground')
levstr='10 m above ground'
ugrd = grb.select(shortName='UGRD', level=levstr)[0].data
ugrd = ugrd * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data
vgrd = vgrd * 1.94384 # convert m/s to kt

# Calculate wind speed
wspd = (ugrd**2+vgrd**2)**.5
'''

#===================================================================================================
print('Plotting 2 m temperature, MSLET and 10 m wind')
#fig_prefix = 'GFSv16'
fig_prefix = conf['model_deny'] + '-' + conf['model_ctl']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 8
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

mpl.rcParams['figure.figsize'] = [8, 5.4]
fig_name = fig_prefix+'.'+'t2m_mslp_wind10m.'+conf['ymdh']+'.'+conf['fhhh'].lower()+'.png'
cbshrink = 0.7
#lonmin = np.min(lon)
#lonmax = np.max(lon)
lonmin = conf['lonmin']
lonmax = conf['lonmax']
lonint = 10.0
#latmin = np.min(lat)
#latmax = np.max(lat)
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

cflevels = np.arange(-4, 4.1, 0.2)
#ctmp = plt.get_cmap('bwr')
#cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name,ctmp(np.linspace(0.04, 0.98, 201)))
#cf = ax.contourf(lon, lat, tmp, levels=cflevels, cmap=cmap, extend='both', transform=transform)

diff = tmp_deny-tmp_ctl
#diff = tmp_deny
cf = ax.contourf(lon, lat, diff, levels=cflevels, cmap='bwr', extend='both')
#cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True, ticks=cflevels[::10])
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, shrink=cbshrink, extendrect=True, ticks=cflevels[::2])

#wb = ax.barbs(lon[::skip,::skip], lat[::skip,::skip], ugrd[::skip,::skip], vgrd[::skip,::skip], length=wblength, linewidth=0.2, color='black', transform=transform,flip_barb=lat[::skip,::skip]<0)

try:
    cslevels = np.arange(-2,2.1,0.1)
    #cs = ax.contour(lon, lat, slp, levels=cslevels, colors='black', linewidths=0.6, transform=transform)
    #cs = ax.contour(lon, lat, slp_deny-slp_ctl, levels=cslevels, colors='black', linewidths=0.6)
    lblevels = np.arange(-2,2.1,0.1)
    #lb = plt.clabel(cs, levels=lblevels, inline_spacing=1, fmt='%d', fontsize=8)
except:
    print('ax.contour failed, continue anyway')

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

#print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
#ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

model_info = conf['model_deny'] + '-' + conf['model_ctl']
#var_info = '2 m Temperature (${^o}$C, shaded), MSLP (hPa), 10 m Wind (kt)'
var_info = '2 m Temperature (${^o}$C, shaded), MSLP (hPa)'
#storm_info = conf['stormName']+conf['stormID']
storm_info = " "
title_center = """{0} {1}
{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_center, loc='center', y=0.99)
title_left = conf['initTime'].strftime('Initialized: %Y%m%d%HZ ')
ax.set_title(title_left, loc='left', y=0.99)
title_right = conf['validTime'].strftime(' Valid: %Y%m%d%HZ') + '(' +  conf['fhhh'] + ')'
ax.set_title(title_right, loc='right', y=0.99)
#footer = os.environ.get('FOOTERgraph','GFS').strip()
#ax.text(1.0,-0.04, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
