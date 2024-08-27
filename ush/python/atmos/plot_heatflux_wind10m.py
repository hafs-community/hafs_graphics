#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric total heat flux and 10-m wind."""

import os

import yaml
import numpy as np
import pandas as pd

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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.atm.'+conf['fhhh']+'.grb2'
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


print('Extracting SHTFL, LHTFL at surface')
shf = grb.select(shortName='SHTFL')[0].data
#shf = gaussian_filter(shf, 5)

lhf = grb.select(shortName='LHTFL')[0].data
#lhf = gaussian_filter(lhf, 5)

# Calculate total heat flux
thf = shf + lhf

print('Extracting UGRD, VGRD at 10 m above ground')
levstr='10 m above ground'
ugrd = grb.select(shortName='UGRD', level=levstr)[0].data
ugrd = ugrd * 1.94384 # convert m/s to kt

vgrd = grb.select(shortName='VGRD', level=levstr)[0].data
vgrd = vgrd * 1.94384 # convert m/s to kt

# Calculate wind speed
wspd = (ugrd**2+vgrd**2)**.5

#===================================================================================================
print('Plotting Enthalpy Flux and 10-m wind')
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
    fig_name = fig_prefix+'.storm.'+'heatflux_wind10m.'+conf['fhhh'].lower()+'.png'
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
    fig_name = fig_prefix+'.'+'heatflux_wind10m.'+conf['fhhh'].lower()+'.png'
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

cflevels = np.linspace(0, 1500, 61)
ctmp = plt.get_cmap('afmhot_r')
cmap = mpl.colors.LinearSegmentedColormap.from_list('sub_'+ctmp.name,ctmp(np.linspace(0, 0.90, 101)))
cf = ax.contourf(lon, lat, thf, cflevels, cmap=cmap, extend='both', transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True, ticks=cflevels[::4])

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
var_info = 'Surface Enthalpy Flux (W/m$^2$, shaded), 10 m Wind (kt)'
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
