#!/usr/bin/env python3

"""This script is to plot out HAFS simulated GOES-R water vapor band-9 brightness temperature."""

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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].upper()+'.'+conf['stormDomain']+'.sat.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting SBTAGR9 grid information')
grb_grid = grb.select(shortName='SBTAGR9')[0].gridDefinitionTemplate

nlon = grb_grid[7]
nlat = grb_grid[8]
blat = grb_grid[11]/1.e6
blon = grb_grid[12]/1.e6
elat = grb_grid[14]/1.e6
elon = grb_grid[15]/1.e6
dlat = grb_grid[16]/1.e6
dlon = grb_grid[17]/1.e6
lat1d = np.linspace(blat, elat, nlat)
if elon > blon:
    lon1d = np.linspace(blon, elon, nlon)
else:
    lon1d = np.linspace(blon, 360.+elon, nlon)
    lon1d = np.mod(lon1d, 360.)

[lon, lat] = np.meshgrid(lon1d, lat1d)

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
#[nlat, nlon] = np.shape(lon)

print('Extracting SBTAGR9')
wv = grb.select(shortName='SBTAGR9')[0].data
wv = wv-273.15 # convert K to deg C
wv = gaussian_filter(wv, 2)

#===================================================================================================
print('Plotting SBTAGR9')
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
    fig_name = fig_prefix+'.storm.'+'goes_wv9.'+conf['fhhh'].lower()+'.png'
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
    fig_name = fig_prefix+'.'+'goes_wv9.'+conf['fhhh'].lower()+'.png'
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

cflevels = [-110.2,-109.2,-108.2,-107.2,-106.2,-105.2,-104.2,-103.2,-102.2,-101.2,-100.2,-99.2,-98.2,-97.2,-96.2,-95.2,-94.2,-93.2,-92.2,-91.2,-90.2,-89.2,-88.2,-87.2,-86.2,-85.2,-84.2,-83.2,-82.2,-81.2,-80.2,-79.2,-78.2,-77.2,-76.2,-75.2,-74.2,-73.2,-72.2,-71.2,-70.2,-69.2,-68.2,-67.2,-66.2,-65.2,-64.2,-63.2,-62.2,-61.2,-60.2,-59.2,-58.2,-57.2,-56.2,-55.2,-54.2,-53.2,-52.2,-51.2,-50.2,-49.2,-48.2,-47.2,-46.2,-45.2,-44.2,-43.2,-42.2,-41.2,-40.2,-39.2,-38.2,-37.2,-36.2,-35.2,-34.2,-33.2,-32.2,-31.2,-30.7,-30.2,-29.7,-29.2,-28.7,-28.2,-27.7,-27.2,-26.7,-26.2,-25.7,-25.2,-24.7,-24.2,-23.7,-23.2,-22.7,-22.2,-21.7,-21.2,-20.7,-20.2,-19.7,-19.2,-18.7,-18.2,-17.7,-17.2,-16.7,-16.2,-15.7,-15.2,-14.7,-14.2,-13.7,-13.2,-12.7,-12.2,-11.7,-11.2,-10.7,-10.2,-9.7,-9.2,-8.7,-8.2,-7.7,-7.2,-6.7,-6.2,-5.7,-5.2,-4.7,-4.2,-3.7,-3.2,-2.7,-2.2,-1.7,-1.2,-0.7,-0.2,0.3,0.8,1.3,1.8,2.3,2.8,3.3,3.8,4.3,4.8,5.3,5.8,6.3,6.8,7.3,7.8,8.3,8.8,9.3,9.8,10.3,10.8,11.3,11.8,12.3,12.8,13.3,13.8,14.3,14.8,15.3,15.8,16.3,16.8,17.3,17.8,18.3,18.8,19.3,19.8,20.3,20.8,21.3,21.8,22.3,22.8,23.3,23.8,24.3,24.8,25.3,25.8,26.3,26.8,27.3,27.8,28.3,28.8,29.3,29.8,30.3,30.8,31.3,31.8,32.3,32.8,33.3,33.8,34.3,34.8,35.3,35.8,36.3,36.8,37.3,37.8,38.3,38.8,39.3,39.8,40.3,40.8,41.3,41.8,42.3,42.8,43.3,43.8,44.3,44.8,45.3,45.8,46.3,46.8,47.3,47.8,48.3,48.8]

cfcolors = [(255,255,255),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(0,0,50),(79,79,79),(99,99,99),(118,118,118),(138,138,138),(157,157,157),(177,177,177),(196,196,196),(216,216,216),(235,235,235),(255,255,255),(79,79,80),(99,99,71),(118,118,62),(138,138,53),(157,157,44),(177,177,36),(196,196,27),(216,216,18),(235,235,9),(255,255,0),(254,0,0),(237,0,0),(220,0,0),(203,0,0),(186,0,0),(168,0,0),(151,0,0),(134,0,0),(117,0,0),(100,0,0),(0,254,0),(0,237,0),(0,220,0),(0,203,0),(0,186,0),(0,168,0),(0,151,0),(0,134,0),(0,117,0),(0,100,0),(0,0,254),(0,0,237),(0,0,220),(0,0,203),(0,0,186),(0,0,168),(0,0,151),(0,0,134),(0,0,117),(0,0,100),(77,127,177),(85,135,185),(92,142,192),(100,150,200),(255,255,255),(255,255,255),(225,225,225),(217,217,217),(210,210,210),(202,202,202),(195,195,195),(187,187,187),(179,179,179),(172,172,172),(164,164,164),(157,157,157),(149,149,149),(141,141,141),(134,134,134),(126,126,126),(119,119,119),(111,111,111),(103,103,103),(96,96,96),(88,88,88),(81,81,81),(73,73,73),(65,65,65),(58,58,58),(50,50,50),(43,43,43),(35,35,35),(75,0,0),(88,9,0),(101,18,0),(114,27,0),(126,36,0),(139,45,0),(152,54,0),(165,63,0),(178,73,0),(191,82,0),(204,91,0),(216,100,0),(229,109,0),(242,118,0),(255,127,0),(225,0,0),(214,0,0),(204,0,0),(193,0,0),(182,0,0),(171,0,0),(161,0,0),(150,0,0),(139,0,0),(129,0,0),(118,0,0),(107,0,0),(96,0,0),(86,0,0),(75,0,0),(34,19,19),(50,23,23),(66,27,27),(81,31,31),(97,35,35),(113,39,39),(129,43,43),(145,47,47),(160,51,51),(176,55,55),(192,59,59),(208,63,63),(223,67,67),(239,71,71),(255,75,75),(200,200,0),(198,198,0),(197,197,0),(195,195,0),(193,193,0),(191,191,0),(190,190,0),(188,188,0),(186,186,0),(185,185,0),(183,183,0),(181,181,0),(179,179,0),(178,178,0),(176,176,0),(174,174,0),(173,173,0),(171,171,0),(169,169,0),(168,168,0),(166,166,0),(164,164,0),(162,162,0),(161,161,0),(159,159,0),(157,157,0),(156,156,0),(154,154,0),(152,152,0),(150,150,0),(149,149,0),(147,147,0),(145,145,0),(144,144,0),(142,142,0),(140,140,0),(138,138,0),(137,137,0),(135,135,0),(133,133,0),(132,132,0),(130,130,0),(128,128,0),(126,126,0),(125,125,0),(123,123,0),(121,121,0),(120,120,0),(118,118,0),(116,116,0),(114,114,0),(113,113,0),(111,111,0),(109,109,0),(108,108,0),(106,106,0),(104,104,0),(103,103,0),(101,101,0),(99,99,0),(97,97,0),(96,96,0),(94,94,0),(92,92,0),(91,91,0),(89,89,0),(87,87,0),(85,85,0),(84,84,0),(82,82,0),(80,80,0),(79,79,0),(77,77,0),(75,75,0),(73,73,0),(72,72,0),(70,70,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(49,49,0),(47,47,0),(46,46,0),(44,44,0),(42,42,0),(41,41,0),(39,39,0),(37,37,0),(35,35,0),(34,34,0),(32,32,0),(30,30,0),(29,29,0),(27,27,0)]

cfcolors = np.divide(cfcolors, 255.)

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, wv, cflevels, cmap=cm, extend='both', norm=norm, transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=np.linspace(-110.,50.,17))

# Add borders and coastlines
#ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')

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
var_info = 'Simulated GOES-R Water Vapor Band-9 Brightness Temperature (deg C)'
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
