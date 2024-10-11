#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric South-North cross section from 1000-100mb at model's storm center (ATCF)."""

import os
import sys

import yaml
import numpy as np
import pandas as pd

import grib2io

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

import cartopy

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
    fig, (ax1) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))
    fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']
    fig_name = fig_prefix+'.storm.'+'crs_sn_reflectivity.'+conf['fhhh'].lower()+'.png'
    ax1.text(0.15,0.5,'No track record found at this time', fontsize=25)
    ax1.tick_params(bottom=False,left=False,labelbottom=False, labelleft=False)
    plt.savefig(fig_name, bbox_inches='tight')
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

lat = grb.select(shortName='NLAT')[0].data
lon = grb.select(shortName='ELON')[0].data
[nlat, nlon] = np.shape(lon)

grblevs=np.arange(100,1001,25)

print('extract levs='+str(grblevs))
for ind, lv in enumerate(grblevs):
  levstr= str(lv)+' mb'
  print('Extracting data at '+levstr)
  refd = grb.select(shortName='REFD', level=levstr)[0].data
  if ind == 0:
    refdtmp=np.zeros((len(grblevs),refd.shape[0],refd.shape[1]))
    refdtmp[ind,:,:]=refd
  refdtmp[ind,:,:]=refd

########    PLOTTING SETTING
idx = find_nearest(clon, clat, lon, lat)

print(idx[0],idx[1])
fig, (ax1) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))

fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']
fig_name = fig_prefix+'.storm.'+'crs_sn_reflectivity.'+conf['fhhh'].lower()+'.png'
cbshrink = 1.0
skip = 20
wblength = 5

idx = find_nearest(clon, clat, lon, lat)

######### RH vort Ta wind plot
cflevels = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75]
cfcolors = ['white','cyan','deepskyblue','blue','lime','limegreen','green',
                        'yellow','gold','orange','red','firebrick','darkred','magenta','darkorchid','purple']

newlats, levs = np.meshgrid(lat[200:600, idx[1]], grblevs)
cs2 = ax1.contourf(newlats, levs, ( refdtmp[:, 200:600 , idx[1]] ), colors=cfcolors, levels=cflevels, extend='max')

##############Modify axis tick label
plt.savefig('for_axis_tmp', bbox_inches='tight')
locs=ax1.get_xticks()
labels = ax1.get_xticklabels()
latlab=[]
for j in range(len(labels)):
  str1=str(labels[j])
  for i in str1.split():
    if i.startswith("Text(") :
      lattmp=float(i.strip('Text(,'))

      if lattmp > 0:
        str2=str(int(lattmp))+'N'
      else :
        str2=str(int(lattmp))+'S'
        str2=str2.strip('-')
      latlab.append(str2)

plt.cla()
fig, (ax1) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))

ax1.set_xticks(locs)
ax1.set_xticklabels(latlab)
#####################
cs2 = ax1.contourf(newlats, levs, ( refdtmp[:, 200:600 , idx[1]] ), colors=cfcolors, levels=cflevels, extend='max')
cb2 = plt.colorbar(cs2, ax=ax1, orientation='vertical', pad=0.02, aspect=50, extendfrac='auto', shrink=cbshrink, extendrect=True, ticks=cflevels)

ax1.set_yscale('log')
ax1.set_ylim(1000,100)
ax1.set_yticks(range(1000, 99, -100))
ax1.set_yticklabels(range(1000, 99, -100))
ax1.set_ylabel('Pressure (hPa)')
ax1.set_xlabel('Latitude')

if clon > 180.:
  clonpr=str(round( (clon-360.),2) ).strip('-')+'W'
else:
  clonpr=str(round(clon,2))+'E'

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'Simulated Radar Reflectivity (dBZ) X-section at '+str(clonpr)
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}
{1}
{2}""".format(model_info,var_info,storm_info)
ax1.set_title(title_left, loc='left', y=0.99)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax1.set_title(title_right, loc='right', y=0.99)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax1.text(1.0,-0.13, footer, fontsize=12, va="top", ha="right", transform=ax1.transAxes)

plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
os.remove('for_axis_tmp.png')

