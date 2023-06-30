#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric East-West cross section from 1000-100mb at model's storm center (ATCF)."""

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
from cartopy.mpl.ticker import (LongitudeLocator, LongitudeFormatter, LongitudeLocator, LongitudeFormatter)

import metpy.calc as mpcalc
import metpy

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

atcffname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+'trak.atcfunix'
atcffile = os.path.join(conf['COMhafs'], atcffname)
print(f'ATCFfile: {atcffile}')
df = pd.read_csv(atcffile,header=None)

tmp1=np.arange(0,df.shape[0])
print(conf['fhour'])

for tind in tmp1:
  if df.loc[tind][5] == conf['fhour']:
    print(tind)
    break
  elif tind == tmp1[len(tmp1)-1] and df.loc[tind][5] != conf['fhour'] :
    print('No record found at forecast hour')
    sys.exit()

def latlon_str2num(string): #Adopted from ATCF 
    """Convert lat/lon string into numbers.""" 
    value = pd.to_numeric(string[:-1], errors='coerce') / 10
    if string.endswith(('N', 'E')):
      return value
    else:
      return -value

clat= latlon_str2num(df.loc[tind][6])
clon= latlon_str2num(df.loc[tind][7])
if clon < 0 :
   clon = clon + 360

print('From ATCF Model TC loc='+str(clat)+' '+str(clon))

def find_nearest(pointx, pointy, gridx, gridy):

    dist = (gridx - pointx)**2 + (gridy - pointy)**2
    idx = np.where(dist == dist.min())
    
    return [idx[0][0], idx[1][0]]

print('Extracting lat, lon')

lat = np.asarray(grb.select(shortName='NLAT')[0].data())
lon = np.asarray(grb.select(shortName='ELON')[0].data())
[nlat, nlon] = np.shape(lon)

grblevs=np.arange(100,1001,25)
fcor=metpy.calc.coriolis_parameter(np.deg2rad(lat))

print('extract levs='+str(grblevs))
for ind, lv in enumerate(grblevs):
  levstr= str(lv)+' mb'
  print('Extracting data at '+levstr)
  rh = grb.select(shortName='RH', level=levstr)[0].data()
  rh.data[rh.mask] = np.nan
  rh[rh<0.] = np.nan
  rh = np.asarray(rh)
  if ind == 0:
    rhtmp=np.zeros((len(grblevs),rh.shape[0],rh.shape[1]))
    rhtmp[ind,:,:]=rh
  rhtmp[ind,:,:]=rh

  tmp = grb.select(shortName='TMP', level=levstr)[0].data()
  tmp.data[tmp.mask] = np.nan
  tmp[tmp<0.] = np.nan
  if ind == 0:
    tmp_anomaly=np.zeros((len(grblevs),tmp.shape[0],tmp.shape[1]))                            
    ptmp=np.zeros((len(grblevs),tmp.shape[0],tmp.shape[1]))
  ptmp[ind,:,:] = tmp*np.power((1000/lv),0.286)
  tmp_mean = np.nanmean(tmp)
  tmp_anomaly[ind,:,:] = tmp - tmp_mean

tmp_anomaly = gaussian_filter(tmp_anomaly,1)

########    PLOTTING SETTING
idx = find_nearest(clon, clat, lon, lat)

print(idx[0],idx[1])
fig, (ax1) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))

fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']
#fig_name = fig_prefix+'.storm.'+'crs_we_rh_tempanomaly_ptemp.'+conf['fhhh'].lower()+'.png'
fig_name = fig_prefix+'.storm.'+'crs_we_rh_tempanomaly.'+conf['fhhh'].lower()+'.png'
cbshrink = 1.0
skip = 20
wblength = 5

idx = find_nearest(clon, clat, lon, lat)

cflevels = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,99]
cfcolors = ['#996515','#a3742c','#ad8444','#b8935b','#c2a373','#ccb28a','#d6c1a1','#e0d1b9','#ebe0d0','#f5f0e8', # Brown https://colorswall.com/palette/26287
            '#ffffff','#d1e6cf','#bbdab7','#a4ce9f','#8dc287','#76b56e','#5fa956','#499d3e','#329026','#1b840e','#008000'] # Green https://colorswall.com/palette/1386
newlons, levs = np.meshgrid(lon[idx[0], 300:700], grblevs)
cs1 = ax1.contourf(newlons, levs, ( rhtmp[:, idx[0], 300:700] ), colors=cfcolors, levels=cflevels, extend='max')
##############Modify axis tick label
plt.savefig('for_axis_tmp', bbox_inches='tight')
locs=ax1.get_xticks()
labels = ax1.get_xticklabels()
lonlab=[]
for j in range(len(labels)):
  str1=str(labels[j])
  for i in str1.split():
    if i.startswith("Text(") :
      lontmp=float(i.strip('Text(,'))
      if lontmp > 180:
        lontmp=lontmp-360

      if lontmp > 0:
        str2=str(int(lontmp))+'E'
      else :
        str2=str(int(lontmp))+'W'
        str2=str2.strip('-')
      lonlab.append(str2)

plt.cla()
fig, (ax1) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))
ax1.set_xticks(locs)
ax1.set_xticklabels(lonlab)
#####################
cs1 = ax1.contourf(newlons, levs, ( rhtmp[:, idx[0], 300:700] ), colors=cfcolors, levels=cflevels, extend='max')
cb1 = plt.colorbar(cs1, ax=ax1, orientation='vertical', pad=0.02, aspect=50, extendfrac='auto', shrink=cbshrink, extendrect=True, ticks=cflevels)

if np.max(tmp_anomaly[:, idx[0], 300:700]) > 2:  #make sure contour can be generated
  cflevels = [2,4,6,8,10,12,14,16,18 ]
  cf2 = ax1.contour(newlons, levs, ( tmp_anomaly[:, idx[0], 300:700] ), cflevels, colors=('r','r','r','r','r','r','r'),linewidths=0.8,linestyles='dashed')
  plt.clabel(cf2, cflevels, fontsize=8,fmt='%2.0f')

if np.min(tmp_anomaly[:, idx[0], 300:700])< -2:
  cflevels = [-8,-6,-4,-2]
  cf2 = ax1.contour(newlons, levs, ( tmp_anomaly[:, idx[0], 300:700] ), cflevels, colors=('b','b','b','b'), linestyles='dashed',linewidths=0.8)
  plt.clabel(cf2, cflevels, fontsize=8,fmt='%2.0f')

cs2levels = np.arange(260,421,5)
cs2 = ax1.contour(newlons, levs, ( ptmp[:, idx[0], 300:700 ] ), levels=cs2levels, colors='k',linewidths=0.8)
plt.clabel(cs2,colors='k',fmt='%4.0f')

ax1.set_yscale('log')
ax1.set_ylim(1000,100)
ax1.set_yticks(range(1000, 99, -100))
ax1.set_yticklabels(range(1000, 99, -100))
ax1.set_ylabel('Pressure (hPa)')
ax1.set_xlabel('Longitude')

if clat < 0:
  clatpr=str(round(clat,2)).strip('-')+'S'
else:
  clatpr=str(round(clat,2))+'N'

title_center = 'RH (%, shaded), Potential T (K, solid), T Anomaly (K, dashed) X-section at '+str(clatpr)
ax1.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax1.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax1.set_title(title_right, loc='right')

plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
os.remove('for_axis_tmp.png')

