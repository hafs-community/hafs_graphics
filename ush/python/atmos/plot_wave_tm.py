#!/usr/bin/env python3

"""This script is to plot out WW3 mean period of combined wind waves and swell."""

import os
import sys

import yaml
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

import xarray as xr
import grib2io

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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
def latlon_str2num(string):
    """Convert lat/lon string into numbers."""
    value = pd.to_numeric(string[:-1], errors='coerce') / 10
    if string.endswith(('N', 'E')):
        return value
    else:
        return -value

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

#===================================================================================================
# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+'ww3.grb2'
grib2file = os.path.join(conf['COMhafs'], fname) 
print(f'grib2 file: {grib2file}')

grb_ww3 = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
#lat,lon = grb_ww3.select(shortName='HTSGW')[int(conf['fhour']/3)].latlons()
lat,lon = grb_ww3.select(shortName='HTSGW')[int(conf['fhour']/3)].grid()

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

lon_adeckk = np.hstack([lon_adeck[lon_adeck<0]+lon_offset,lon_adeck[lon_adeck>0]-lon_offset])

print('Extracting mean period of combined wind waves and swell')
mwp = grb_ww3.select(shortName='MWSPER')[int(conf['fhour']/3)].data

print('Extracting wave mean direction')
wmd = grb_ww3.select(shortName='WWSDIR')[int(conf['fhour']/3)].data

#hgt = gaussian_filter(hgt, 5)

#===================================================================================================
print('Plotting Direction of Combined Wind Waves and Swell')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']

# Set default figure parameters
mpl.rcParams['figure.figsize'] = [8, 8]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 8
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8

nhour = int((int(conf['fhhh'][1:])/3))
okfhour = conf['fhhh'][1:] == fhour
if conf['stormDomain'] == 'storm':
    if len(lon_adeck[okfhour])!=0 and len(lat_adeck[okfhour])!=0:
        mpl.rcParams['figure.figsize'] = [6, 6]
        fig_name = fig_prefix+'.storm.'+'wave_tm.'+conf['fhhh'].lower()+'.png'
        cbshrink = 0.9
        #lon_adeckk = np.hstack([lon_adeck[lon_adeck<0]+lon_offset,lon_adeck[lon_adeck>0]-lon_offset])
        lonmin = np.min(lon_adeckk[int(conf['fhour']/3)]) - 5
        lonmax = np.max(lon_adeckk[int(conf['fhour']/3)]) + 5
        latmin = np.min(lat_adeck[int(conf['fhour']/3)]) - 5
        latmax = np.max(lat_adeck[int(conf['fhour']/3)]) + 5
        lonint = 2.0
        latint = 2.0
        skip = 20
        wblength = 4.5
    else:
        print('There is not latitude or longitude for the center of the storm at this forecast hour. Exiting plotting script')
        sys.exit()

else:
    mpl.rcParams['figure.figsize'] = [8, 5.4]
    fig_name = fig_prefix+'.'+'wave_tm.'+conf['fhhh'].lower()+'.png'
    cbshrink = 0.6
    lonmin = np.min(lon)
    lonmax = np.max(lon)
    lonint = 10.0
    latmin = np.min(lat)
    latmax = np.max(lat)
    latint = 10.0
    skip = round(lon.shape[0]/360)*10
    wblength = 4

myproj = ccrs.PlateCarree(lon_offset)
transform = ccrs.PlateCarree(lon_offset)

# create figure and axes instances
fig = plt.figure()
ax = plt.axes(projection=myproj)
ax.axis('scaled')

# v5 hand picked jet colors
cflevels = [0,2,           # blue
            4,6,8,       # cyan
            9,10,11,12,  # green
            13,14,15,16, # yellow
            17,18,19,    # orange
            20,21,22]    # red

cslevels = cflevels
cclevels = cflevels[1:-1]

cm0 = 'jet'
cmap = plt.get_cmap(cm0)
cfcolors = [cmap(20),cmap(70),                         # blue
            cmap(90),cmap(100),cmap(110),              # cyan
            cmap(120),cmap(130),cmap(140),cmap(150),   # green
            cmap(160),cmap(170),cmap(180),cmap(190),   # yellow
            cmap(200),cmap(210),cmap(220),             # orange
            cmap(230),cmap(240),cmap(250)]             # red

try:
    #cf = ax.contourf(lon, lat, mwp, levels=cflevels, colors=cfcolors, extend='max', transform=transform)
    cf = ax.contourf(lon, lat, mwp, levels=cflevels, colors=cfcolors, transform=transform)
    cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=30, shrink=cbshrink, extendrect=True, ticks=cclevels)
except:
    print('ax.contourf failed, continue anyway')

print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)

try:
    cs = ax.contour(lon, lat, mwp, levels=cslevels, colors='black', linewidths=0.6, transform=transform)
    #lb = plt.clabel(cs, levels=cslevels, inline_spacing=1, fontsize=8)
except:
    print('ax.contour failed, continue anyway')

if conf['stormDomain'] == 'storm':
    ns = 7
    xkey = 0.06
    ykey = -0.07
    ytext = -0.1
    sc = 30
else:
    ns = 30
    xkey = 0.2
    ykey = -0.11
    ytext = -0.17
    sc = 40

try:
    q = ax.quiver(lon[::ns,::ns], lat[::ns,::ns], np.cos(wmd[::ns,::ns]*np.pi/180), np.sin(wmd[::ns,::ns]*np.pi/180), scale=sc)
    ax.quiverkey(q,xkey,ykey,3,label='Direction of Combined Wind Waves and Swell Unscaled ',labelpos = 'E',fontproperties = matplotlib.font_manager.FontProperties(size=8))
except:
    print('ax.quiver failed, continue anyway')

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

oklon = np.logical_and(lon[0,:] >= lonmin,lon[0,:] <= lonmax)
oklat = np.logical_and(lat[:,0] >= latmin,lat[:,0] <= latmax)
if np.logical_and(len(np.where(oklon)[0])!=0,len(np.where(oklat)[0])!=0):
    max_mwp = np.nanmax(mwp[oklat,:][:,oklon])
else:
    max_mwp = np.nan

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'Mean Period of Combined Wind Waves and Swell (s), Max = '+str(np.round(max_mwp,2))+' s'
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}
{1}
{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_left, loc='left', y=0.99)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax.text(1.0,ytext, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)

