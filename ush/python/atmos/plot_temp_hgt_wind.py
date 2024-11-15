#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric temperature, geopotential height,
and wind figures on standard layers (e.g., 850, 700, 500, 300, 200 hPa)."""

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
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.'+conf['stormDomain']+'.atm.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
lat = grb.select(shortName='NLAT')[0].data
lon = grb.select(shortName='ELON')[0].data
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

levstr=str(conf['standardLayer'])+' mb'
print('Extracting HGT, TMP, UGRD, VGRD, at '+levstr)
hgt = grb.select(shortName='HGT', level=levstr)[0].data
hgt = hgt * 0.1 # convert meter to decameter
hgt = gaussian_filter(hgt, 5)

tmp = grb.select(shortName='TMP', level=levstr)[0].data
tmp = tmp - 273.15 # convert K to degC
tmp = gaussian_filter(tmp, 2)

ugrd = grb.select(shortName='UGRD', level=levstr)[0].data
ugrd = ugrd * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data
vgrd = vgrd * 1.94384 # convert m/s to kt

#===================================================================================================
print('Plotting HGT, TMP, UGRD, VGRD, at '+levstr)
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
    fig_name = fig_prefix+'.storm.'+'temp_hgt_wind.'+str(conf['standardLayer'])+'mb.'+conf['fhhh'].lower()+'.png'
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
    fig_name = fig_prefix+'.'+'temp_hgt_wind.'+str(conf['standardLayer'])+'mb.'+conf['fhhh'].lower()+'.png'
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

if conf['standardLayer'] == 200:
    cflevels = np.linspace(-70, -20, 101)
    cslevels=np.arange(1080,1290,12)
elif conf['standardLayer'] == 300:
    cflevels = np.linspace(-60, -10, 101)
    cslevels=np.arange(780,1020,12)
elif conf['standardLayer'] == 500:
    cflevels = np.linspace(-40, 10, 101)
    cslevels=np.arange(480,600,6)
elif conf['standardLayer'] == 700:
    cflevels = np.linspace(-30, 30, 121)
    cslevels=np.arange(210,330,3)
elif conf['standardLayer'] == 850:
    cflevels = np.linspace(-20, 40, 121)
    cslevels=np.arange(60,180,3)
else:
    cflevels = np.linspace(-60, 30, 181)
    cslevels=np.arange(-50,4000,5)

myproj = ccrs.PlateCarree(lon_offset)
transform = ccrs.PlateCarree(lon_offset)

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

#ctmp = plt.get_cmap('gist_ncar')
#cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name, ctmp(np.linspace(0.10, 0.98, 201)))
ctmp = plt.get_cmap('nipy_spectral')
cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name, ctmp(np.linspace(0.04, 0.98, 201)))
cf = ax.contourf(lon, lat, tmp, levels=cflevels, cmap=cmap, extend='both', transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=cflevels[::10])

lat_nh = lat[lat[:,0]>=0,:]
lon_nh = lon[lat[:,0]>=0,:]
ugrd_nh = ugrd[lat[:,0]>=0,:]
vgrd_nh = vgrd[lat[:,0]>=0,:]

lat_sh = lat[lat[:,0]<0,:]
lon_sh = lon[lat[:,0]<0,:]
ugrd_sh = ugrd[lat[:,0]<0,:]
vgrd_sh = vgrd[lat[:,0]<0,:]

wb = ax.barbs(lon_nh[::skip,::skip], lat_nh[::skip,::skip], ugrd_nh[::skip,::skip], vgrd_nh[::skip,::skip],
              length=wblength, linewidth=0.2, color='black', transform=transform,flip_barb=False)
wb = ax.barbs(lon_sh[::skip,::skip], lat_sh[::skip,::skip], ugrd_sh[::skip,::skip], vgrd_sh[::skip,::skip],
              length=wblength, linewidth=0.2, color='black', transform=transform,flip_barb=True)

try:
    cs = ax.contour(lon, lat, hgt, levels=cslevels, colors='black', linewidths=0.6, transform=transform)
#    lb = plt.clabel(cs, levels=cslevels, inline_spacing=1, fmt='%d', fontsize=8)
except:
    print('ax.contour failed, continue anyway')

#plt.tight_layout()

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
var_info = str(conf['standardLayer'])+' hPa Temperature (${^o}$C, shaded), Height (dam), Wind (kt)'
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
