#!/usr/bin/env python3

"""This script is to plot out HAFS simulated SSMIS F17 microwave 91GHz brightness temperature."""

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

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.sat.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting SSMS1717 grid information')
grb_grid = grb.select(shortName='SSMS1717')[0].gridDefinitionTemplate
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

print('Extracting SSMS1717')
mw = grb.select(shortName='SSMS1717')[0].data
#mw = np.asarray(mw)-273.15 # convert K to deg C
mw = gaussian_filter(mw, 2)

#===================================================================================================
print('Plotting SSMS1717')
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
    fig_name = fig_prefix+'.storm.'+'ssmisf17_mw91ghz.'+conf['fhhh'].lower()+'.png'
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
    fig_name = fig_prefix+'.'+'ssmisf17_mw91ghz.'+conf['fhhh'].lower()+'.png'
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

cflevels = [180,180.5672,181.1345,181.7017,182.2689,182.8361,183.4034,183.9706,184.5378,185.105,185.6723,186.2395,186.8067,187.3739,187.9412,188.5084,189.0756,189.6429,190.2101,190.7773,191.3445,191.9118,192.479,193.0462,193.6134,194.1807,194.7479,195.3151,195.8824,196.4496,197.0168,197.584,198.1513,198.7185,199.2857,199.8529,200.4202,200.9874,201.5546,202.1218,202.6891,203.2563,203.8235,204.3908,204.958,205.5252,206.0924,206.6597,207.2269,207.7941,208.3613,208.9286,209.4958,210.063,210.6303,211.1975,211.7647,212.3319,212.8992,213.4664,214.0336,214.6008,215.1681,215.7353,216.3025,216.8697,217.437,218.0042,218.5714,219.1387,219.7059,220.2731,220.8403,221.4076,221.9748,222.542,223.1092,223.6765,224.2437,224.8109,225.3782,225.9454,226.5126,227.0798,227.6471,228.2143,228.7815,229.3487,229.916,230.4832,231.0504,231.6176,232.1849,232.7521,233.3193,233.8866,234.4538,235.021,235.5882,236.1555,236.7227,237.2899,237.8571,238.4244,238.9916,239.5588,240.1261,240.6933,241.2605,241.8277,242.395,242.9622,243.5294,244.0966,244.6639,245.2311,245.7983,246.3655,246.9328,247.5,248.0672,248.6345,249.2017,249.7689,250.3361,250.9034,251.4706,252.0378,252.605,253.1723,253.7395,254.3067,254.8739,255.4412,256.0084,256.5756,257.1429,257.7101,258.2773,258.8445,259.4118,259.979,260.5462,261.1134,261.6807,262.2479,262.8151,263.3824,263.9496,264.5168,265.084,265.6513,266.2185,266.7857,267.3529,267.9202,268.4874,269.0546,269.6218,270.1891,270.7563,271.3235,271.8908,272.458,273.0252,273.5924,274.1597,274.7269,275.2941,275.8613,276.4286,276.9958,277.563,278.1303,278.6975,279.2647,279.8319,280.3992,280.9664,281.5336,282.1008,282.6681,283.2353,283.8025,284.3697,284.937,285.5042,286.0714,286.6387,287.2059,287.7731,288.3403,288.9076,289.4748,290.042,290.6092,291.1765,291.7437,292.3109,292.8782,293.4454,294.0126,294.5798,295.1471,295.7143,296.2815,296.8487,297.416,297.9832,298.5504,299.1176,299.6849,300.2521,300.8193,301.3866,301.9538,302.521,303.0882,303.6555,304.2227,304.7899,305.3571,305.9244,306.4916,307.0588,307.6261,308.1933,308.7605,309.3277,309.895,310.4622,311.0294,311.5966,312.1639,312.7311,313.2983,313.8655,314.4328,315]

cfcolors = [(255,255,255),(252,251,249),(250,246,242),(247,242,236),(245,238,229),(242,233,223),(240,229,216),(237,224,210),(234,220,203),(232,216,197),(229,211,190),(227,207,184),(224,203,178),(222,198,171),(219,194,165),(217,189,158),(214,185,152),(211,181,145),(209,176,139),(206,172,132),(204,168,126),(201,163,119),(199,159,113),(196,155,107),(193,150,100),(191,146,94),(188,141,87),(186,137,81),(183,133,74),(181,128,68),(178,124,61),(176,120,55),(173,115,49),(170,111,42),(168,107,36),(165,102,29),(165,99,26),(167,97,25),(169,95,25),(171,92,24),(173,90,24),(175,88,23),(177,86,23),(179,84,22),(181,82,22),(183,80,21),(185,77,20),(187,75,20),(189,73,19),(191,71,19),(193,69,18),(195,67,18),(197,65,17),(199,62,17),(201,60,16),(203,58,16),(205,56,15),(207,54,15),(209,52,14),(211,50,14),(213,47,13),(215,45,13),(217,43,12),(219,41,12),(221,39,11),(223,37,11),(225,35,10),(227,32,9),(229,30,9),(231,28,8),(233,26,8),(235,24,7),(237,22,7),(239,20,6),(241,17,6),(243,15,5),(245,13,5),(247,11,4),(249,9,4),(251,7,3),(236,195,57),(238,199,53),(239,203,49),(240,207,45),(241,212,41),(243,216,37),(244,220,33),(245,223,30),(246,225,28),(246,227,26),(247,229,24),(248,231,22),(248,233,20),(249,235,19),(250,238,17),(250,240,15),(251,242,13),(251,244,11),(252,246,9),(253,248,7),(253,250,5),(254,252,3),(255,254,1),(169,246,1),(137,241,2),(133,240,2),(130,238,2),(126,236,2),(122,234,2),(120,232,2),(116,231,2),(113,229,2),(109,227,2),(105,226,2),(103,224,2),(99,223,2),(96,221,2),(92,219,2),(88,217,2),(85,215,2),(82,214,2),(79,212,2),(75,211,2),(71,209,2),(68,207,2),(65,206,2),(62,204,2),(58,202,2),(54,200,2),(51,198,2),(48,197,2),(45,196,2),(41,194,2),(37,192,2),(34,190,2),(31,189,2),(27,187,2),(24,185,2),(20,183,2),(17,181,2),(11,199,120),(6,216,252),(6,210,250),(6,205,248),(6,199,246),(6,193,244),(6,187,242),(6,182,240),(6,176,238),(6,170,236),(6,165,234),(6,159,232),(6,153,230),(6,148,228),(6,142,226),(6,136,225),(6,130,223),(6,125,221),(6,119,219),(7,113,217),(7,108,215),(7,102,213),(7,96,211),(7,90,209),(7,85,207),(7,79,205),(7,73,203),(7,68,201),(7,62,199),(7,56,197),(7,50,195),(7,45,193),(7,39,192),(7,33,190),(7,28,188),(7,22,186),(7,16,184),(7,11,182),(14,8,183),(28,7,187),(41,7,191),(55,6,195),(68,6,199),(82,6,203),(95,5,207),(109,5,211),(122,4,215),(136,4,219),(149,3,223),(163,3,228),(176,3,232),(190,2,236),(203,2,240),(217,1,244),(233,1,248),(251,0,254),(237,0,237),(221,0,221),(208,0,208),(196,0,196),(183,0,183),(173,0,173),(162,0,162),(151,0,151),(140,0,140),(129,0,129),(118,0,118),(107,0,107),(96,0,96),(85,0,85),(74,0,74),(58,0,58),(30,0,30),(5,2,5),(34,31,34),(54,52,54),(61,58,61),(67,65,67),(74,72,74),(81,78,81),(87,85,87),(94,92,94),(101,99,101),(107,105,107),(114,112,114),(122,120,122),(131,130,131),(141,139,141),(150,149,150),(160,159,160),(169,168,169),(179,178,179),(188,187,188),(198,197,198),(207,207,207),(217,216,217),(226,226,226),(236,236,236),(245,245,245),(255,255,255)]

cfcolors = np.divide(cfcolors, 255.)

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)

cf = ax.contourf(lon, lat, mw, cflevels, cmap=cm, extend='both', norm=norm, transform=transform)
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True,
                  ticks=np.linspace(180.,310.,14))

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
var_info = 'Simulated SSMIS F17 H 91 GHz Microwave Brightness Temperature (K)'
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
