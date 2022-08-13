#!/usr/bin/env python3
# Created by Bin Liu, NOAA/NWS/NCEP/EMC, 07/2022
"""
This script is to plot out ATCF track, intensity (including vmax and pmin)
figures. Configurable options are read in from the plotATCF.yml file.
"""
import os
import sys
import logging
import math
import datetime

import yaml
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeLocator, LongitudeFormatter, LatitudeLocator, LatitudeFormatter)

#matplotlib.use('agg')
#mpl.use('agg')

def hurricane_marker():
    """Create the hurricane marker."""
    theta = np.linspace(0, 2*np.pi, 17)
    xh = np.cos(theta)
    yh = np.sin(theta)
    ye = np.e*yh
    ym = np.concatenate([ye[12:17], yh[0:9], ye[8:3:-1], ye[4:9], yh[8:17], ye[16:11:-1]])
    xm = np.concatenate([xh[12:17], xh[0:9], xh[8:3:-1], xh[4:9], xh[8:17], xh[16:11:-1]])
    hm = np.vstack((xm,ym))
    hm = np.transpose(hm)
    cm = [1] + [2]*(len(hm)-2) + [2]
    return mpath.Path(hm, cm, closed=True)

def latlon_str2num(string):
    """Convert lat/lon string into numbers."""
    value = pd.to_numeric(string[:-1], errors='coerce') / 10
    if string.endswith(('N', 'E')):
        return value
    else:
        return -value

def main():
    """Parse the plotATCF.yml configure file, read in and manipulate abdeck
    files as pandas dataframes, and plot hurricane track/intensity figures."""

    # Parse the yaml config file
    print('Parse the config file: plotATCF.yml:')
    with open('plotATCF.yml', 'rt') as f:
        conf = yaml.safe_load(f)
    conf['stormNumber']=conf['stormID'][0:2]
    print(conf)
    for i, marker in enumerate(conf['techMarkers']):
        if marker == 'hr':
            conf['techMarkers'][i] = hurricane_marker()
    # Set Cartopy data_dir location
    cartopy.config['data_dir'] = conf['cartopyDataDir']

    # Details about the ATCF format can be seen from: https://www.nrlmry.navy.mil/atcf_web/docs/database/new/abdeck.txt
    cols = ['basin', 'number', 'ymdh', 'technum', 'tech', 'tau', 'lat', 'lon', 'vmax', 'mslp', 'type',
            'rad', 'windcode', 'rad1', 'rad2', 'rad3', 'rad4', 'pouter', 'router', 'rmw', 'gusts', 'eye',
            'subregion', 'maxseas', 'initials', 'dir', 'speed', 'stormname', 'depth',
            'seas', 'seascode', 'seas1', 'seas2', 'seas3', 'seas4', 'userdefined',
            'userdata1', 'userdata2', 'userdata3', 'userdata4', 'userdata5', 'userdata6', 'userdata7', 'userdata8',
            'userdata9', 'userdata10', 'userdata11', 'userdata12', 'userdata13', 'userdata14', 'userdata15', 'userdata16']

    # Read in adeckFile as pandas dataFrame
    print('Read in adeckFile ...')
    adeck = pd.read_csv(conf['adeckFile'], index_col=False, names=cols, dtype=str, header=None, skipinitialspace=True)
    # Read in bdeckFile as pandas dataFrame
    print('Read in bdeckFile ...')
    bdeck = pd.read_csv(conf['bdeckFile'], index_col=False, names=cols, dtype=str, header=None, skipinitialspace=True)

    print('Combining and processing abdeck into atcf data frame ...')
    atcf = pd.concat([adeck, bdeck])
    cols = ['tau', 'vmax', 'mslp', 'rad1', 'rad2', 'rad3', 'rad4', 'pouter', 'router', 'rmw',
            'gusts', 'eye', 'maxseas', 'dir', 'speed', 'seas1', 'seas2', 'seas3', 'seas4']
    atcf[cols] = atcf[cols].apply(pd.to_numeric, errors='coerce')
    atcf['lat'] = atcf['lat'].apply(latlon_str2num)
    atcf['lon'] = atcf['lon'].apply(latlon_str2num)
    atcf['vmax'] = atcf['vmax'].apply(lambda x: x if x>0 else np.nan)
    atcf['mslp'] = atcf['mslp'].apply(lambda x: x if x>800 else np.nan)
    atcf['init_time'] = pd.to_datetime(atcf['ymdh'], format='%Y%m%d%H', errors='coerce')
    atcf['valid_time'] = pd.to_timedelta(atcf['tau'], unit='h') + atcf['init_time']

    fhhh = np.arange(0, conf['forecastLength']+6, 6)
    xinit = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
    xtime = xinit+pd.to_timedelta(fhhh, unit='h')

    print('Extracting adeck records for desired techs ...')
    af = atcf[ atcf['valid_time'].isin(xtime) & (atcf['ymdh'] == conf['ymdh']) &
               (atcf['tech'].isin(conf['techModels'])) & (~atcf['tech'].isin(['BEST'])) ].copy()

    print('Extracting bdeck records ...')
    bf = atcf[atcf['valid_time'].isin(xtime) & atcf['tech'].isin(['BEST'])].copy()

    print('Recalculate tau for bdeck for desired forecast cycle ...')
    dtime = bf['valid_time']-xinit
    bf['tau'] = dtime.apply(lambda x: (x.days*86400+x.seconds)/3600)

    print('Combining af and bf ...')
    df = pd.concat([af, bf])

    # Set default figure parameters
    mpl.rcParams['figure.figsize'] = [8, 8]
    mpl.rcParams['figure.dpi'] = 150
    mpl.rcParams['axes.titlesize'] = 13
    mpl.rcParams['axes.labelsize'] = 12
    mpl.rcParams['xtick.labelsize'] = 11
    mpl.rcParams['ytick.labelsize'] = 11
    mpl.rcParams['legend.fontsize'] = 10
    mpl.rcParams['legend.handlelength'] = 1.2

    # Prepare xticks and xticklabels for vmax and pmin plots
    if conf['forecastLength'] > 126:
        xticks = np.arange(0, conf['forecastLength'], 24)
    else:
        xticks = np.arange(0, conf['forecastLength'], 12)
    dateticks = xinit+pd.to_timedelta(xticks, unit='h')
    xticklabels = []
    for i,x in enumerate(xticks):
        if i%2==0:
            xticklabels.append(str(x)+'\n'+dateticks[i].strftime('%m/%d/%HZ'))
        else:
            xticklabels.append(str(x))

    # Storm track
    print('Plotting storm track ...')
    latlonrange = 0.6
    if (df['lon'].max() - df['lon'].min()) > 180:
        map_projection = ccrs.PlateCarree(180.)
        df['lon'] = df['lon'].apply(lambda x: x+360. if x < 0. else x)
    else:
        map_projection = ccrs.PlateCarree(0.)

    # Optimize lon/lat range and tick
    minLon = df['lon'].min()
    maxLon = df['lon'].max()
    meanLon = (minLon + maxLon) / 2.0
    disLon = (maxLon-minLon)*latlonrange

    minLat = df['lat'].min()
    maxLat = df['lat'].max()
    disLat = (maxLat-minLat)*latlonrange
    meanLat = (minLat + maxLat) / 2.0

    disLon = max([disLon, disLat, 10.])
    disLat = max([disLon, disLat, 10.])
    minLon = meanLon - disLon
    maxLon = meanLon + disLon
    minLat = max([-90., meanLat - disLat])
    maxLat = min([ 90., meanLat + disLat])

    lonmin = math.floor(minLon/5)*5.0
    lonmax = math.ceil(maxLon/5)*5.0
    latmin = math.floor(minLat/5)*5.0
    latmax = math.ceil(maxLat/5)*5.0

    if disLon > 40.:
        llint = 20.
    elif disLon > 20.:
        llint = 10.
    else:
        llint = 5.
    lontick = np.arange(lonmin, lonmax, llint)
    lattick = np.arange(latmin, latmax, llint)
    lontick[lontick>180.] = lontick[lontick>180.] - 360.

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1, projection=map_projection)
    n = len(conf['techModels'])
    for i, model in enumerate(conf['techModels']):
        print(f'Plotting {model} track')
        pf = df[df['tech']==model]
        ax.plot(pf['lon'], pf['lat'], linestyle='solid', linewidth=1.5, clip_on=False, zorder=(n-i)*10,
                color=conf['techColors'][i], alpha=1.0, marker=conf['techMarkers'][i],
                markersize=conf['techMarkerSizes'][i], markerfacecolor=conf['techColors'][i],
                markeredgecolor=conf['techColors'][i], label=conf['techLabels'][i], transform=ccrs.Geodetic())
        if conf['catInfo']:
            for lon, lat, vmax in zip(pf['lon'], pf['lat'], pf['vmax']):
                if vmax >= 137.:
                    strCat = '5'
                elif vmax >= 113.:
                    strCat = '4'
                elif vmax >= 96.:
                    strCat = '3'
                elif vmax >= 83.:
                    strCat = '2'
                elif vmax >= 64.:
                    strCat = '1'
                elif vmax >= 34.:
                    strCat = 'S'
                else:
                    strCat = 'D'
                ax.text(lon, lat, strCat, color='white', size=6, fontweight="bold",
                        va='center', ha='center', zorder=(n-i)*10+5)
            t=ax.text(0.02, 0.98, 'D: TD  S: TS  1-5: Hurricane Cat 1-5',
                      fontsize=10, fontweight='normal', va='top', ha='left', transform=ax.transAxes,
                      bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
        if conf['timeInfo']:
            for tau, lon, lat in zip(pf['tau'], pf['lon'], pf['lat']):
                if int(round(tau))%24 == 0 and int(round(tau)) != 0:
                    strTau = str(int(round(tau)))
                    ax.text(lon, lat+0.3, strTau, color=conf['techColors'][i], fontsize=10,
                            va='bottom', ha='center', zorder=(n-i)*10+5)
            t=ax.text(0.98, 0.98, '24,48,72,...: Forecast Hours',
                      fontsize=10, fontweight='normal', va='top', ha='right', transform=ax.transAxes,
                      bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))

    # Add borders and coastlines
    ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

   #gl = ax.gridlines(crs=map_projection, draw_labels=True, linewidth=0.3, color='0.3', alpha=0.6, linestyle=(0, (5, 10)))
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.3', alpha=0.6, linestyle=(0, (5, 10)))
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 12, 'color': 'black'}
    gl.ylabel_style = {'size': 12, 'color': 'black'}

    print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=map_projection)

    handles, labels = ax.get_legend_handles_labels()
    if len(handles) > 8:
        idx = [0,1,2,3,4,5,6,-1]
        ax.legend([handles[i] for i in idx], [labels[i] for i in idx], bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    else:
        ax.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    #ax.set_title('Storm Track', loc='center', y=1.15)
    ax.set_title(conf['stormModel']+' '+conf['stormName']+conf['stormID'], loc='left', y=1.08)
    ax.set_title('Init: '+conf['ymdh']+'Z', loc='right', y=1.08)

    figname = conf['stormName']+conf['stormID']+'.'+conf['ymdh']+'.track.png'
    plt.savefig(figname)
    plt.close(fig)

    # Storm intensity vmax
    print('Plotting vmax ...')
    fig, ax = plt.subplots(figsize=(8,5))
    n = len(conf['techModels'])
    for i, model in enumerate(conf['techModels']):
        print(f'Plotting {model}')
        pf = df[df['tech']==model]
        ax.plot(pf['tau'], pf['vmax'], linestyle='solid', linewidth=1.5, clip_on=False, zorder=n-i,
                color=conf['techColors'][i], alpha=1.0, marker=conf['techMarkers'][i],
                markersize=0.8*conf['techMarkerSizes'][i], markerfacecolor=conf['techColors'][i],
                markeredgecolor=conf['techColors'][i], label=conf['techLabels'][i])

    ax.set_xlim(0, conf['forecastLength'])
    ymin = max([math.floor(df['vmax'].min()/10.)*10.-10., 0.])
    ymax = math.ceil(df['vmax'].max()/10.)*10.+10.
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator(n=2))
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(n=2))

    ratio = 0.5
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    ax.grid(linewidth=0.3, color='0.3', alpha=0.6, linestyle=(0, (5, 10)))

    handles, labels = ax.get_legend_handles_labels()
    if len(handles) > 8:
        idx=[0,1,2,3,4,5,6,-1]
        ax.legend([handles[i] for i in idx], [labels[i] for i in idx], bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    else:
        ax.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    #ax.set_title('Storm Intensity Vmax (kt)', loc='center', y=1.15)
    ax.set_title(conf['stormModel']+' '+conf['stormName']+conf['stormID'], loc='left', y=1.08)
    ax.set_title('Init: '+conf['ymdh']+'Z', loc='right', y=1.08)
    ax.set_xlabel('Forecast Hour and Valid Time (MM/DD/HH in UTC)')
    ax.set_ylabel('Maximum 10-m Wind (kt)')

    if conf['catRef']:
        vmaxRef = [34., 64., 83., 96., 113., 137.]
        vmaxCat = ['TS', 'H1', 'H2', 'H3', 'H4', 'H5']
        for i in range(len(vmaxRef)):
            if vmaxRef[i] > ymin and vmaxRef[i] < ymax:
                ax.axhline(y=vmaxRef[i], color='0.2', linewidth=0.5, linestyle=(0, (5, 5)), alpha=0.6)
                ax.text(conf['forecastLength']+1, vmaxRef[i], vmaxCat[i], size=11, va='center', ha='left')

    figname = conf['stormName']+conf['stormID']+'.'+conf['ymdh']+'.Vmax.png'
    plt.savefig(figname)
    plt.close(fig)

    # Storm intensity Pmin
    print('Plotting pmin ...')
    fig, ax = plt.subplots(figsize=(8,5))
    n = len(conf['techModels'])
    for i, model in enumerate(conf['techModels']):
        print(f'Plotting {model}')
        pf = df[df['tech']==model]
        ax.plot(pf['tau'], pf['mslp'], linestyle='solid', linewidth=1.5, clip_on=False, zorder=n-i,
                color=conf['techColors'][i], alpha=1.0, marker=conf['techMarkers'][i],
                markersize=0.8*conf['techMarkerSizes'][i], markerfacecolor=conf['techColors'][i],
                markeredgecolor=conf['techColors'][i], label=conf['techLabels'][i])

    ax.set_xlim(0, conf['forecastLength'])
    ymin = max([math.floor(df['mslp'].min()/10.)*10.-10., 0.])
    ymax = math.ceil(df['mslp'].max()/10.)*10.+10.
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator(n=2))
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(n=2))

    ratio = 0.5
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    ax.grid(linewidth=0.3, color='0.3', alpha=0.6, linestyle=(0, (5, 10)))

    handles, labels = ax.get_legend_handles_labels()
    if len(handles) > 8:
        idx = [0,1,2,3,4,5,6,-1]
        ax.legend([handles[i] for i in idx], [labels[i] for i in idx], bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    else:
        ax.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .100),
                  loc='lower left', ncol=8, mode='expand', borderaxespad=0., frameon=False)
    #ax.set_title('Storm Intensity Pmin (hPa)', loc='center', y=1.15)
    ax.set_title(conf['stormModel']+' '+conf['stormName']+conf['stormID'], loc='left', y=1.08)
    ax.set_title('Init: '+conf['ymdh']+'Z', loc='right', y=1.08)
    ax.set_xlabel('Forecast Hour and Valid Time (MM/DD/HH in UTC)')
    ax.set_ylabel('Minimum Sea Level Pressure (hPa)')

    if conf['catRef']:
        pminRef = [920., 945., 965., 980., 995., 1005.]
        pminCat = ['H5', 'H4', 'H3', 'H2', 'H1', 'TS']
        for i in range(len(pminRef)):
            if pminRef[i] > ymin and pminRef[i] < ymax:
                ax.axhline(y=pminRef[i], color='0.2', linewidth=0.5, linestyle=(0, (5, 5)), alpha=0.6)
                ax.text(conf['forecastLength']+1, pminRef[i], pminCat[i], size=11, va='center', ha='left')

    figname = conf['stormName']+conf['stormID']+'.'+conf['ymdh']+'.Pmin.png'
    plt.savefig(figname)
    plt.close(fig)

if __name__=='__main__':
    sys.exit(main())
