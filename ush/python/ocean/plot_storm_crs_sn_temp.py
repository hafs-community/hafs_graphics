#!/usr/bin/env python3

"""This scrip plots a latitudinal transect of temperature. """

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
# Conversion from geographic longitude and latitude to HYCOM convention
def HYCOM_coord_to_geo_coord(lonh,lath):
    lonh = np.asarray(lonh)
    if np.ndim(lonh) > 0:
        long = [ln-360 if ln>=180 else ln for ln in lonh]
    else:
        long = [lonh-360 if lonh>=180 else lonh][0]
    latg = lath
    return long, latg

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
    adeck_name = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.trak.atcfunix'
    adeck_file = os.path.join(conf['COMhafs'],adeck_name)

    fhour,lat_adeck,lon_adeck,init_time,valid_time = get_adeck_track(adeck_file)

    print('lon_adeck = ',lon_adeck)
    print('lat_adeck = ',lat_adeck)

#================================================================
# Read ocean files

oceanf = glob.glob(os.path.join(conf['COMhafs'],'*f006.nc'))[0].split('/')[-1].split('.')

ocean = [f for f in oceanf if f == 'hycom' or f == 'mom6'][0]

if ocean == 'mom6':
    fname000 =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.mom6.'+'f000.nc'
    fname =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.mom6.'+conf['fhhh']+'.nc'

if ocean == 'hycom':
    fname000 =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.hycom.3z.'+'f000.nc'
    fname =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.hycom.3z.'+conf['fhhh']+'.nc'

ncfile000 = os.path.join(conf['COMhafs'], fname000)
nc000 = xr.open_dataset(ncfile000)
ncfile = os.path.join(conf['COMhafs'], fname)
nc = xr.open_dataset(ncfile)

if ocean == 'mom6':
    varr000 = np.asarray(nc000['temp'][0,:,:,:])
    varr = np.asarray(nc['temp'][0,:,:,:])
    mldd = np.asarray(nc['MLD_0125'][0,:,:])
    zl = np.asarray(nc['z_l'])
    lon = np.asarray(nc.xh)
    lat = np.asarray(nc.yh)

if ocean == 'hycom':
    varr000 = np.asarray(nc000['temperature'][0,:,:,:])
    varr = np.asarray(nc['temperature'][0,:,:,:])
    mldd = np.asarray(nc['mixed_layer_thickness'][0,:,:])
    zl = np.asarray(nc['Z'])
    lonh = np.asarray(nc.Longitude)
    lath = np.asarray(nc.Latitude)
    lon, lat = HYCOM_coord_to_geo_coord(lonh,lath)

lonmin_raw = np.min(lon)
lonmax_raw = np.max(lon)
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

#================================================================
# Constrain lon limits between -180 and 180 so it does not conflict with the cartopy projection PlateCarree
lon_ticks = np.copy(lon)
lon_ticks[lon_ticks>180] = lon_ticks[lon_ticks>180] - 360
lon_ticks[lon_ticks<-180] = lon_ticks[lon_ticks<-180] + 360

#lon[lon>180] = lon[lon>180] - 360
#lon[lon<-180] = lon[lon<-180] + 360

#================================================================
#%% Latitudinal transect
okfhour = conf['fhhh'][1:] == fhour
if len(lon_adeck[okfhour])==0 or len(lat_adeck[okfhour])==0:
    print('There is not latitude or longitude for the center of the storm at this forecast hour. Exiting plot_storm_crs_sn_temp.py')
    sys.exit()
else:
    lon_eye = lon_adeck[okfhour][0]
    xpos = int(np.round(np.interp(lon_eye,lon,np.arange(len(lon)))))
    
    var000 = varr000[:,:,xpos]
    var = varr[:,:,xpos]
    mld = mldd[:,xpos]

    diff = var - var000
    
    #================================================================
    # Temp
    lat_eye = lat_adeck[okfhour][0]

    kw = dict(levels=np.arange(15,31.1,0.5))
    fig,ax = plt.subplots(figsize=(8,4))
    ctr = ax.contourf(lat,-zl,var,cmap='Spectral_r',**kw,extend='both')
    cbar = fig.colorbar(ctr,extendrect=True)
    #cbar.set_label('$^oC$',fontsize=14)
    cs = ax.contour(lat,-zl,var,[26],colors='k')
    ax.plot(lat,-mld,'-',color='green')
    ax.plot(np.tile(lat_eye,len(zl)),-zl,'-k')
    ax.clabel(cs,cs.levels,inline=True,fmt='%1.1f',fontsize=10)
    ax.set_ylim([-300,0])
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Latitude')
    
    if lon_eye >= 0:
        hemis = 'E'
    else:
        hemis = 'W'
        
    model_info = os.environ.get('TITLEgraph','').strip()
    var_info = 'Temperature($^oC$) X-section at  ' + str(np.round(lon_eye,2)) + ' ' + hemis
    storm_info = conf['stormName']+conf['stormID']
    title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
    ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
    title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
    ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
    footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
    ax.text(1.0,-0.2, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)
    
    pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm.crs_sn_temp'+'.'+conf['fhhh'].lower()+'.png'
    plt.savefig(pngFile,bbox_inches='tight',dpi=150)
    plt.close()
    
    #================================================================
    # Temp - Temp000
    kw = dict(levels=np.arange(-4,4.1,0.2))
    fig,ax = plt.subplots(figsize=(8,4))
    ctr = ax.contourf(lat,-zl,diff,cmap='seismic',**kw,extend='both')
    cbar = fig.colorbar(ctr,extendrect=True)
    cbar.set_label('$^oC$',fontsize=14)
    cs = ax.contour(lat,-zl,diff,[0],colors='grey',alpha=0.3)
    ax.plot(lat,-mld,'-',color='green')
    ax.plot(np.tile(lat_eye,len(zl)),-zl,'-k')
    ax.clabel(cs,cs.levels,inline=True,fmt='%1.1f',fontsize=10)
    ax.set_ylim([-300,0])
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Latitude')
    
    model_info = os.environ.get('TITLEgraph','').strip()
    var_info = 'Temperature Difference($^oC$) X-section at ' + str(np.round(lon_eye,2)) + ' ' + hemis + '. Min dT = ' + str(np.round(np.nanmin(diff),2))
    storm_info = conf['stormName']+conf['stormID']
    title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
    ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
    title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
    ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
    footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
    ax.text(1.0,-0.2, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)
    
    pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm.crs_sn_temp'+'.change.'+conf['fhhh'].lower()+'.png'
    plt.savefig(pngFile,bbox_inches='tight',dpi=150)
    plt.close()
