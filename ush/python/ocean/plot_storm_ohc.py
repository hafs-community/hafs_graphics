#!/usr/bin/env python3

"""This scrip plots the ocean heat content for an area 500 km around the storm eye. """ 

import os
import sys
import glob
import yaml

import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
  
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from eos80 import dens

from geo4HYCOM import haversine

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
# Calculate ocean heat content
def ohc(temp,salt,zl):
    cp = 3985 #Heat capacity in J/(kg K)
    zl_array = np.reshape(np.tile(zl,(temp.shape[1]*temp.shape[2],1)).T,(temp.shape[0],temp.shape[1],temp.shape[2]))
    no26 = temp < 26
    temp[no26] = np.nan
    salt[no26] = np.nan
    density = dens(salt,temp,zl_array)
    rho0 = np.nanmean(density,axis=0)
    zl_array_fac = (zl_array[0:-1,:,:] + zl_array[1:,:,:])/2
    zero_array = np.zeros((1,temp.shape[1],temp.shape[2]))
    bott_array = np.ones((1,temp.shape[1],temp.shape[2]))* zl_array_fac[-1,0,0] + (zl[-1] - zl[-2])
    zl_array_face = np.vstack((zero_array,zl_array_fac,bott_array))
    dz_array = np.diff(zl_array_face,axis=0)
    ohc = np.abs(cp * rho0 * np.nansum((temp-26)*dz_array,axis=0)) * 10**(-7) # in kJ/cm^2
  
    return ohc

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

# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

#================================================================
# Get lat and lon from adeck file

if conf['trackon']=='yes':
    adeck_name = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
    adeck_file = os.path.join(conf['COMhafs'],adeck_name)

    fhour,lat_adeck,lon_adeck,init_time,valid_time = get_adeck_track(adeck_file)

    print('lon_adeck = ',lon_adeck)
    print('lat_adeck = ',lat_adeck)

#================================================================
# Read ocean files

oceanf = glob.glob(os.path.join(conf['COMhafs'],'*f006.nc'))[0].split('/')[-1].split('.')

ocean = [f for f in oceanf if f == 'hycom' or f == 'mom6'][0]

if ocean == 'mom6':
    fname000 =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.mom6.'+'f000.nc'
    fname =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.mom6.'+conf['fhhh']+'.nc'

if ocean == 'hycom':
    fname000 =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.hycom.3z.f000'+'.nc'
    fname =  conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.hycom.3z.'+conf['fhhh']+'.nc'

ncfile000 = os.path.join(conf['COMhafs'], fname000)
nc000 = xr.open_dataset(ncfile000)
ncfile = os.path.join(conf['COMhafs'], fname)
nc = xr.open_dataset(ncfile)

if ocean == 'mom6':
    temp000 = np.asarray(nc000['temp'][0,:,:,:])
    salt000 = np.asarray(nc000['so'][0,:,:,:])
    zl000 = np.asarray(nc000['z_l'])
    temp = np.asarray(nc['temp'][0,:,:,:])
    salt = np.asarray(nc['so'][0,:,:,:])
    zl = np.asarray(nc['z_l'])
    lon = np.asarray(nc.xh)
    lat = np.asarray(nc.yh)

if ocean == 'hycom':
    varr000 = np.asarray(nc000['ocean_heat_content'][0,:,:])
    varr = np.asarray(nc['ocean_heat_content'][0,:,:])
    lon = np.asarray(nc.Longitude)
    lat = np.asarray(nc.Latitude)

lonmin_raw = np.min(lon)
lonmax_raw = np.max(lon)
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

#================================================================
# Constrain lon limits between -180 and 180 so it does not conflict with the cartopy projection PlateCarree
lon[lon>180] = lon[lon>180] - 360
sort_lon = np.argsort(lon)
lon = lon[sort_lon]

# define grid boundaries
lonmin_new = np.min(lon)
lonmax_new = np.max(lon)
latmin = np.min(lat)
latmax = np.max(lat)
print('new lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

# Shift central longitude so the Southern Hemisphere and North Indin Ocean domains are plotted continuously
if np.logical_and(lonmax_new >= 90, lonmax_new <=180):
    central_longitude = 90
else:
    central_longitude = -90
print('central longitude: ',central_longitude)

# sort var according to the new longitude
if ocean == 'mom6':
    temp000 = temp000[:,:,sort_lon]
    salt000 = salt000[:,:,sort_lon]
    temp = temp[:,:,sort_lon]
    salt = salt[:,:,sort_lon]

if ocean == 'hycom':
    varr000 = varr000[:,sort_lon]
    varr = varr[:,sort_lon]

#================================================================
# Calculate ocean heat content
if ocean == 'mom6':
    varr000 = ohc(temp000,salt000,zl)
    varr = ohc(temp,salt,zl)

#================================================================
var_name= 'ohc'
units = '($kJ/cm^2$)'

Rkm=500    # search radius [km]
lns,lts = np.meshgrid(lon,lat)
dummy = np.ones(lns.shape)

nhour = int((int(conf['fhhh'][1:])/3))
if lat_adeck[nhour] < (latmax+5.0):
    dR=haversine(lns,lts,lon_adeck[nhour],lat_adeck[nhour])/1000.
    dumb=dummy.copy()
    dumb[dR>Rkm]=np.nan

    var = varr*dumb

    dvar = np.asarray(varr - varr000)*dumb

    # create figure and axes instances
    fig = plt.figure(figsize=(6,6))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=central_longitude))
    ax.axis('scaled')
    
    cflevels = np.linspace(0, 180, 37)
    cmap = plt.get_cmap('Spectral_r')
    cf = ax.contourf(lon, lat, var, levels=cflevels, cmap=cmap, extend='max', transform=ccrs.PlateCarree())
    ax.contour(lon, lat, var, levels=[60], colors='k',alpha=0.5, linewidths=0.5, transform=ccrs.PlateCarree())
    cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=20, shrink=0.6, extendrect=True, ticks=cflevels[::4])
    cb.ax.tick_params(labelsize=8)
    
    if conf['trackon']=='yes':
        lon_adeck[np.logical_or(lon_adeck<lonmin_new,lon_adeck>lonmax_new)] = np.nan
        ax.plot(lon_adeck,lat_adeck,'-ok',markersize=2,alpha=0.4,transform=ccrs.PlateCarree(central_longitude=0))
    
        if nhour <= len(fhour):
            ax.plot(lon_adeck[nhour],lat_adeck[nhour],'ok',markersize=10,alpha=0.6,markerfacecolor='None',transform=ccrs.PlateCarree(central_longitude=0))
       
            if np.logical_and(lon_adeck[nhour]-5.5 > lonmin_new,lon_adeck[nhour]+5.5 < lonmax_new):
                mnmx="(min,max)="+"(%6.1f"%np.nanmin(var)+","+"%6.1f)"%np.nanmax(var)
                plt.text(lon_adeck[nhour]-2.15-central_longitude,lat_adeck[nhour]-4.75,mnmx,fontsize=8,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5))
                ax.set_extent([lon_adeck[nhour]-5.5,lon_adeck[nhour]+5.5,lat_adeck[nhour]-5,lat_adeck[nhour]+5],crs=ccrs.PlateCarree())
            else:
                print('Longitude track limits are out of the ocean domain')
    
    # Add gridlines and labels
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, 2))
    gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, 2))
    gl.xlabel_style = {'size': 8, 'color': 'black'}
    gl.ylabel_style = {'size': 8, 'color': 'black'}
    
    # Add borders and coastlines
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

    model_info = os.environ.get('TITLEgraph','').strip()
    var_info = 'Ocean Heat Content ($kJ/cm^2$)'
    storm_info = conf['stormName']+conf['stormID']
    title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
    ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
    title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
    ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
    footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
    ax.text(1.0,-0.08, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

    pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm_'+var_name+'.'+conf['fhhh'].lower()+'.png'
    plt.savefig(pngFile,bbox_inches='tight',dpi=150)
    plt.close("all")
    
    # create figure and axes instances
    fig = plt.figure(figsize=(6,6))
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=central_longitude))
    ax.axis('scaled')
    
    cflevels = np.linspace(-50, 50, 21)
    cmap = plt.get_cmap('RdBu_r')
    cf = ax.contourf(lon, lat, dvar, levels=cflevels, cmap=cmap, extend='both', transform=ccrs.PlateCarree())
    ax.contour(lon, lat, dvar, cflevels, colors='grey',alpha=0.5, linewidths=0.5, transform=ccrs.PlateCarree())
    cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=20, shrink=0.6, extendrect=True, ticks=cflevels[::4])
    cb.ax.tick_params(labelsize=8)
    
    if conf['trackon']=='yes':
        lon_adeck[np.logical_or(lon_adeck<lonmin_new,lon_adeck>lonmax_new)] = np.nan
        ax.plot(lon_adeck,lat_adeck,'-ok',markersize=2,alpha=0.4,transform=ccrs.PlateCarree(central_longitude=0))
        if nhour <= len(fhour):
            ax.plot(lon_adeck[nhour],lat_adeck[nhour],'ok',markersize=10,alpha=0.6,markerfacecolor='None',transform=ccrs.PlateCarree(central_longitude=0))
       
            if np.logical_and(lon_adeck[nhour]-5.5 > lonmin_new,lon_adeck[nhour]+5.5 < lonmax_new):
                mnmx="(min,max)="+"(%6.1f"%np.nanmin(dvar)+","+"%6.1f)"%np.nanmax(dvar)

                plt.text(lon_adeck[nhour]-2.15-central_longitude,lat_adeck[nhour]-4.75,mnmx,fontsize=8,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5))
                ax.set_extent([lon_adeck[nhour]-5.5,lon_adeck[nhour]+5.5,lat_adeck[nhour]-5,lat_adeck[nhour]+5],crs=ccrs.PlateCarree())
            else:
                print('Longitude track limits are out of the ocean domain')
    
    # Add gridlines and labels
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, 2))
    gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, 2))
    gl.xlabel_style = {'size': 8, 'color': 'black'}
    gl.ylabel_style = {'size': 8, 'color': 'black'}
    
    # Add borders and coastlines
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

    model_info = os.environ.get('TITLEgraph','').strip()
    var_info = 'Ocean Heat Content Change ($kJ/cm^2$)'
    storm_info = conf['stormName']+conf['stormID']
    title_left = """{0}\n{1}\n{2}""".format(model_info,var_info,storm_info)
    ax.set_title(title_left, loc='left', y=0.99,fontsize=8)
    title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
    ax.set_title(title_right, loc='right', y=0.99,fontsize=8)
    footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
    ax.text(1.0,-0.08, footer, fontsize=8, va="top", ha="right", transform=ax.transAxes)

    pngFile = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']+'.ocean.storm_'+var_name+'.change.'+conf['fhhh'].lower()+'.png'
    plt.savefig(pngFile,bbox_inches='tight',dpi=150)
    plt.close("all")
    
