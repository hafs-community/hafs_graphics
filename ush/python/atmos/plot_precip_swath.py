#!/usr/bin/env python3

"""This script plots out the HAFS total rainfall swath for a 126 hours forecast, based on the 3-hours accumulated precipitation from the grid01 files."""

import os
import sys
import logging
import math
import datetime
import glob

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

#===================================================================================================
def latlon_str2num(string):
    """Convert lat/lon string into numbers."""
    value = pd.to_numeric(string[:-1], errors='coerce') / 10
    if string.endswith(('N', 'E')):
        return value
    else:
        return -value

#===================================================================================================
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

#===================================================================================================
def get_R_and_tan_theta_around_N_degrees_from_eye(N,lon, lat, lon_track, lat_track):

    xlim = [lon_track-N,lon_track+N]
    ylim = [lat_track-N,lat_track+N]

    oklon = np.logical_and(lon>xlim[0],lon<xlim[1])
    oklat = np.logical_and(lat>ylim[0],lat<ylim[1])

    lat_lon_matrix = np.stack((np.ravel(lon),np.ravel(lat)),axis=1).T

    R = np.empty(lat_lon_matrix.shape[1])
    R[:] = np.nan
    tan_theta = np.empty(lat_lon_matrix.shape[1])
    tan_theta[:] = np.nan
    cos_theta = np.empty(lat_lon_matrix.shape[1])
    cos_theta[:] = np.nan
    sin_theta = np.empty(lat_lon_matrix.shape[1])
    sin_theta[:] = np.nan
    for i in np.arange(lat_lon_matrix.shape[1]):
        R[i],tan_theta[i],cos_theta[i], sin_theta[i] = Haversine(lat_track,lon_track,lat_lon_matrix[1,i],lat_lon_matrix[0,i])

    return oklat, oklon, R, tan_theta, cos_theta, sin_theta

#===================================================================================================
def Haversine(lat1,lon1,lat2,lon2):
    """
    This uses the haversine formula to calculate the great-circle distance
    between two points that is, the shortest distance over the earth surface
    giving an the-crow-flies~@~Y distance between the points
    (ignoring any hills they fly over, of course!).
    Haversine formula:
    a = sin²(~T~F/2) + cos ~F1 ~K~E cos ~F2 ~K~E sin²(~Tλ/2)
    c = 2 ~K~E atan2( ~H~Za, ~H~Z(1~H~Ra) )
    d = R ~K~E c
    where   ~F is latitude, λ is longitude, R is earth's radius
    (mean radius = 6,371km). Note that angles need to be in radians to pass to
    trig functions!
    """

    R = 6371.0088
    lat1,lon1,lat2,lon2 = map(np.radians, [lat1,lon1,lat2,lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2) **2
    c = 2 * np.arctan2(a**0.5, (1-a)**0.5)
    d = R * c

    tan_theta = dlat/dlon
    cos_theta = (dlon*180/np.pi)*111.111/d
    sin_theta = (dlat*180/np.pi)*111.111/d

    return d, tan_theta, cos_theta, sin_theta

#===================================================================================================
# Parse the yaml config file
print('Parse the config file: plot_atmos.yml:')
with open('plot_atmos.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']

#===================================================================================================
# Get lat and lon from adeck file
adeck_name = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
adeck_file = os.path.join(conf['COMhafs'],adeck_name)

fhour,lat_adeck,lon_adeck,init_time,valid_time = get_adeck_track(adeck_file)

print('lon_adeck = ',lon_adeck)
print('lat_adeck = ',lat_adeck)

#===================================================================================================
# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+'parent'+'.atm.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())

# The lon range in grib2 is typically between 0 and 360
# Cartopy's PlateCarree projection typically uses the lon range of -180 to 180
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

# first coordinate transformation to geographic -180 to 180 coordinates
lon[lon>180] = lon[lon>180] - 360.
#sort_lon = np.ravel(np.argsort(lon))
sort_lon = np.argsort(lon[0,:])
#lon = np.reshape(np.ravel(lon)[sort_lon],(lon.shape[0],lon.shape[1]))
lon = lon[:,sort_lon]
print('new lonlat limit to -180 to 180 convention: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

print('Extracting APCP')
accumulation_time = grb.select(shortName='APCP')[-1].timeRangeOfStatisticalProcess
apcp = grb.select(shortName='APCP')[-1].data()
apcp.data[apcp.mask] = np.nan
apcp_raw = np.asarray(apcp)*0.0393701  # convert kg/m^2 to in 
#apcp = np.reshape(np.ravel(apcp)[sort_lon],(lon.shape[0],lon.shape[1]))
apcp = apcp_raw[:,sort_lon]
#apcp = gaussian_filter(apcp, 2)

#===================================================================================================
print('Obtaining the mask along the forecast track, around 500 km from the storm center')
N = 8 # 8 degrees around track
freq = np.arange(0,43,3)
apcp_masked0 = np.empty((len(freq),apcp.shape[0],apcp.shape[1]))
apcp_masked0[:] = np.nan
for i,r in enumerate(freq):
    print(r)
    lon_track = lon_adeck[r]
    lat_track = lat_adeck[r]
    oklat, oklon, R, _, _, _ = get_R_and_tan_theta_around_N_degrees_from_eye(N,lon,lat,lon_track,lat_track)
    okR = R <= 500
    okR_matrix = np.reshape(okR,(lat.shape[0],lat.shape[1]))
    apcp_mask = apcp*okR_matrix
    apcp_mask[apcp_mask == 0] = np.nan
    print(np.nanmax(apcp_mask))
    apcp_masked0[i,:,:] = apcp_mask

apcp_masked = np.nanmean(apcp_masked0,axis=0)

#===================================================================================================
print('Plotting APCP ')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [6, 6]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

mpl.rcParams['figure.figsize'] = [6, 6]

# second coordinate transformation to plot
lon = np.asarray(grb.select(shortName='ELON')[0].data())
lonn = lon
if abs(np.max(lonn) - 360.) < 10.:
    lonn[lonn>180] = lonn[lonn>180] - 360.
    lon_offset = 0.
else:
    lon_offset = 180.
lonn = lonn - lon_offset
print('lon_offset = ',lon_offset)

myproj = ccrs.PlateCarree(lon_offset)
transform = ccrs.PlateCarree(lon_offset)

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('equal')

cflevels = [0,0.5,               # white
            1,2,3,            # green
            4,8,           # yellow
            16,               # orange
            24,             # red
            32,40]           # magenta

cfcolors = ['white','whitesmoke',
            'lawngreen','mediumseagreen', 'green',         # green
            'yellow','gold',                      # yellow
            'orange',           # red
            'red','magenta']  # purple

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)  

try:
    #cf = ax.contourf(lonn, lat, apcp_raw, cflevels, cmap=cm, norm=norm,transform=transform)
    cf = ax.contourf(lonn[:,sort_lon], lat, apcp_masked, cflevels, cmap=cm, norm=norm,transform=transform)
    cbshrink = 1.0
    cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,ticks=[0,0.5,1,2,3,4,8,16,24,32])
    cb.ax.set_yticklabels(['0','0.5','1','2','3','4','8','16','24','32'])
except:
    print('ax.contourf failed, continue anyway')

try:
    cs = ax.contour(lonn[:,sort_lon], lat, apcp_masked, [1,2,3,4,8,16,24,32], colors='grey', linewidths=0.7, transform=transform)
    #lblevels = cflevels
    #lb = plt.clabel(cs, [0,0.5,1,2,3,4,8,16,24,32], inline_spacing=1, fmt='%d', fontsize=6)
except:
    print('ax.contour failed, continue anyway')

lon_adeckk = np.hstack([lon_adeck[lon_adeck<0]+lon_offset,lon_adeck[lon_adeck>0]-lon_offset])
ax.plot(lon_adeckk, lat_adeck, '.-k',markersize=1,linewidth=0.5)

# Add borders and coastlines
ax.add_feature(cfeature.BORDERS, linewidth=0.5, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.STATES, linewidth=0.5, facecolor='none', edgecolor='gray')
ax.add_feature(cfeature.COASTLINE, linewidth=1.0, facecolor='none', edgecolor='dimgray')

#gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.6, color='lightgray', alpha=0.6, linestyle=(0, (5, 10)))
gl = ax.gridlines(draw_labels=True, linewidth=0.6, color='lightgray', alpha=0.6, linestyle=(0, (5, 10)))
gl.top_labels = False
gl.right_labels = False
lonint = 5
latint = 5
gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, lonint))
gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, latint))
gl.xlabel_style = {'size': 8, 'color': 'black'}
gl.ylabel_style = {'size': 8, 'color': 'black'}

lonmin = np.min(lon_adeckk) - 10
lonmax = np.max(lon_adeckk) + 10
latmin = np.min(lat_adeck) - 10
latmax = np.max(lat_adeck) + 10
print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

title_center = 'Total Rainfall (in)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')

title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right',x=1.05)

#plt.show() 
fig_name = fig_prefix+'.storm.'+'precip.swath.'.lower()+conf['fhhh']+'.png'
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
