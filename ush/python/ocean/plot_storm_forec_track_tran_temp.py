#!/usr/bin/env python3

"""This scrip plots an along forecast track transect of temperature. """

import os
import sys
import glob
import yaml

import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

#================================================================
def latlon_str2num(string):
    """Convert lat/lon string into numbers."""
    value = pd.to_numeric(string[:-1], errors='coerce') / 10
    if string.endswith(('N', 'E')):
        return value
    else:
        return -value

#================================================================
#================================================================
def get_adeck_track(adeck_file):

    cols = ['basin', 'number', 'ymdh', 'technum', 'tech', 'tau', 'lat', 'lon', 'vmax', 'mslp', 'type','rad', 'windcode', 'rad1', 'rad2', 'rad3', 'rad4', 'pouter', 'router', 'rmw', 'gusts', 'eye','subregion', 'maxseas', 'initials', 'dir', 'speed', 'stormname', 'depth','seas', 'seascode', 'seas1', 'seas2', 'seas3', 'seas4', 'userdefined','userdata1', 'userdata2', 'userdata3', 'userdata4', 'userdata5', 'userdata6', 'userdata7', 'userdata8','userdata9', 'userdata10', 'userdata11', 'userdata12', 'userdata13', 'userdata14', 'userdata15', 'userdata16']

    # Read in adeckFile as pandas dataFrame
    print('Read in adeckFile ...')
    adeck = pd.read_csv(adeck_file, index_col=False, names=cols, dtype=str, header=None, skipinitialspace=True)

    adeck['lat'] = adeck['lat'].apply(latlon_str2num)
    adeck['lon'] = adeck['lon'].apply(latlon_str2num)
    #adeck['vmax'] = adeck['vmax'].apply(lambda x: x if x>0 else np.nan)
    #adeck['mslp'] = adeck['mslp'].apply(lambda x: x if x>800 else np.nan)
    adeck['init_time'] = pd.to_datetime(adeck['ymdh'], format='%Y%m%d%H', errors='coerce')
    adeck['valid_time'] = pd.to_timedelta(adeck['tau'].apply(pd.to_numeric, errors='coerce'), unit='h') + adeck['init_time']

    fhour, ind = np.unique(adeck['tau'],return_index=True)
    lat_adeck = np.asarray(adeck['lat'][ind])
    lon_adeck = np.asarray(adeck['lon'][ind])
    init_time = np.asarray(adeck['init_time'][ind])
    valid_time = np.asarray(adeck['valid_time'][ind])

    return fhour,lat_adeck,lon_adeck,init_time,valid_time

#================================================================
# Parse the yaml config file
print('Parse the config file: plot_ocean.yml:')
with open('plot_ocean.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

#================================================================
# Get lat and lon from adeck file

if conf['trackon']=='yes':
    adeck_name = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
    adeck_file = os.path.join(conf['COMhafs'],adeck_name)

    fhour,lat_adeck,lon_adeck,init_time,valid_time = get_adeck_track(adeck_file)

    print('lon_adeck = ',lon_adeck)
    print('lat_adeck = ',lat_adeck)
#================================================================
# Read MOM6 file

fname003 =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.mom6.'+'f003.nc'
fname =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.mom6.'+conf['fhhh']+'.nc'

ncfile003 = os.path.join(conf['COMhafs'], fname003)
nc003 = xr.open_dataset(ncfile003)
ncfile = os.path.join(conf['COMhafs'], fname)
nc = xr.open_dataset(ncfile)

lon = np.asarray(nc.xh)
lat = np.asarray(nc.yh)
lonmin_raw = np.min(lon)
lonmax_raw = np.max(lon)
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

#================================================================
#%% temp along storm path
lon_adeck_interp = np.interp(lat,lat_adeck,lon_adeck,left=np.nan,right=np.nan)
lat_adeck_interp = np.copy(lat)
lat_adeck_interp[np.isnan(lon_adeck_interp)] = np.nan

lon_adeck_int = lon_adeck_interp[np.isfinite(lon_adeck_interp)]
lat_adeck_int = lat_adeck_interp[np.isfinite(lat_adeck_interp)]
lon_adeck_int[0:len(lon_adeck_int)] = lon_adeck_int
lat_adeck_int[0:len(lat_adeck_int)] = lat_adeck_int

oklon = np.round(np.interp(lon_adeck_int,lon,np.arange(len(lon)))).astype(int)
oklat = np.round(np.interp(lat_adeck_int,lat,np.arange(len(lat)))).astype(int)

zl = np.asarray(nc['z_l'])
var003 = np.empty((len(zl),len(lon_adeck_int)))
var003[:] = np.nan 
var = np.empty((len(zl),len(lon_adeck_int)))
var[:] = np.nan 
for x in np.arange(len(lon_adeck_int)):
    var003[:,x] = np.asarray(nc003['temp'][0,:,oklat[x],oklon[x]])
    var[:,x] = np.asarray(nc['temp'][0,:,oklat[x],oklon[x]])

diff = var - var003

#================================================================
# Temp
kw = dict(levels=np.arange(15,31.1,0.5))
fig,ax = plt.subplots(figsize=(8,4))
ctr = ax.contourf(lat[oklat],-zl,var,cmap='Spectral_r',**kw,extend='both')
cbar = fig.colorbar(ctr,extendrect=True)
cbar.set_label('$^oC$',fontsize=14)
cs = ax.contour(lat[oklat],-zl,var,[26],colors='k')
ax.clabel(cs,cs.levels,inline=True,fmt='%1.1f',fontsize=10)
ax.set_ylim([-300,0])
ax.set_ylabel('Depth (m)')
ax.set_xlabel('Latitude')

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'Along Forecast Track Transect Temperature ($^oC$)'
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax.text(1.0,-0.1, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm.forec_track_transect_temp'+'.'+conf['fhhh'].lower()+'.png'
plt.savefig(pngFile,bbox_inches='tight',dpi=150)
plt.close()

#================================================================
# Temp - Temp003
kw = dict(levels=np.arange(-4,4.1,0.2))
fig,ax = plt.subplots(figsize=(8,4))
ctr = ax.contourf(lat[oklat],-zl,diff,cmap='seismic',**kw,extend='both')
cbar = fig.colorbar(ctr,extendrect=True)
cbar.set_label('$^oC$',fontsize=14)
cs = ax.contour(lat[oklat],-zl,diff,[0],colors='k',alpha=0.3)
ax.clabel(cs,cs.levels,inline=True,fmt='%1.1f',fontsize=10)
ax.set_ylim([-300,0])
ax.set_ylabel('Depth (m)')
#ax.set_xlabel('Latitude')
ax.set_xlabel('Latitude \n dT min = ' + str(np.round(np.nanmin(diff),2)),fontsize=14)

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'Along Forecast Track Transect Temperature Difference ($^oC$)'
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax.text(1.0,-0.1, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm.forec_track_transect_temp_diff'+'.'+conf['fhhh'].lower()+'.png'
plt.savefig(pngFile,bbox_inches='tight',dpi=150)
plt.close()

