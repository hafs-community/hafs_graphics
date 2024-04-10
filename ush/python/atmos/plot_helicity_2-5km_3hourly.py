#!/usr/bin/env python3

"""This script plots out the HAFS total rainfall swath for a 126 hours forecast """

import os
import sys

import yaml
import numpy as np
import pandas as pd

import grib2io
from netCDF4 import Dataset

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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
    a = sin²(~T~F/2) + cos ~F1 ~K~E cos ~F2 ~K~E sin²(~T?/2)
    c = 2 ~K~E atan2( ~H~Za, ~H~Z(1~H~Ra) )
    d = R ~K~E c
    where   ~F is latitude, ? is longitude, R is earth's radius
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
#conf['validTime'] = conf['initTime'] + conf['fcstTime']

#===================================================================================================
# Get lat and lon from adeck file
adeck_name = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
adeck_file = os.path.join(conf['COMhafs'],adeck_name)

fhour,lat_adeck,lon_adeck,init_time,valid_time = get_adeck_track(adeck_file)
if len(fhour) < 43:
  print("The last ATCF record: "+fhour[len(fhour)-1])

#===================================================================================================
# Set Cartopy data_dir location
cartopy.config['data_dir'] = conf['cartopyDataDir']
print(conf)

fnameswath = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.swath.'+'grb2'
grib2file = os.path.join(conf['COMhafs'], fnameswath)
print(f'grib2file: {grib2file}')
grbswath = grib2io.open(grib2file,mode='r')

fnamef00 = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.atm.f000.'+'grb2'
grib2file = os.path.join(conf['COMhafs'], fnamef00)
print(f'grib2file: {grib2file}')
grbf00 = grib2io.open(grib2file,mode='r')

print('Extracting lat, lon')
lat = grbf00.select(shortName='NLAT')[0].data
lon = grbf00.select(shortName='ELON')[0].data
# The lon range in grib2 is typically between 0 and 360
# Cartopy's PlateCarree projection typically uses the lon range of -180 to 180
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
if abs(np.max(lon) - 360.) < 10.:
    lon[lon>180] = lon[lon>180] - 360.
    lon_offset = 0.
else:
    #lon_offset = 180.
    lon_offset = 360.
lon = lon - lon_offset
print('new lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))
[nlat, nlon] = np.shape(lon)

print('Extracting Helicity')
varlen=grbswath.select(shortName='UPHL', level='5000-2000 m above ground')
print(len(varlen))
varshape=grbswath.select(shortName='UPHL', level='5000-2000 m above ground')[0].data
print(varshape.shape)

for frame in range(len(varlen)):
  #accumulation_time = grbswath.select(shortName='WIND')[frame].timeRangeOfStatisticalProcess
  conf['fhhh'] = "{:03d}".format((frame+1)*3)
  conf['fcstTime'] = pd.to_timedelta(int(conf['fhhh']), unit='h')
  conf['validTime'] = conf['initTime'] + conf['fcstTime']

  uphl = grbswath.select(shortName='UPHL', level='5000-2000 m above ground')[frame].data
  
  #===================================================================================================
  print('Obtaining the mask along the forecast track, around 500 km from the storm center')
  N = 8 # 8 degrees around track
  freq = np.arange(frame,frame+1,1)
  uphl_masked0 = np.empty((len(freq),uphl.shape[0],uphl.shape[1]))
  uphl_masked0[:] = np.nan
  print(freq)
  for i,r in enumerate(freq+1):
      print(i,r)
      lon_track = lon_adeck[r]
      lat_track = lat_adeck[r]
      print(lon_track,lat_track)
      oklat, oklon, R, _, _, _ = get_R_and_tan_theta_around_N_degrees_from_eye(N,lon,lat,lon_track,lat_track)
      okR = R <= 500
      okR_matrix = np.reshape(okR,(lat.shape[0],lat.shape[1]))
      uphl_mask = uphl*okR_matrix
      uphl_mask[uphl_mask == 0] = np.nan
      uphl_masked0[i,:,:] = uphl_mask
  
  uphl_masked = np.nanmean(uphl_masked0,axis=0)
  
  #===================================================================================================
  print('Plotting helicity 2-5km')
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
  lonmin = np.min(lon_adeck) - 10 
  lonmax = np.max(lon_adeck) + 10 
  latmin = np.min(lat_adeck) - 10 
  latmax = np.max(lat_adeck) + 10 
  
  myproj = ccrs.PlateCarree(lon_offset)
  transform = ccrs.PlateCarree(lon_offset)
  
  # create figure and axes instances
  fig = plt.figure()
  ax = plt.axes(projection=myproj)
  ax.axis('equal')
  
  cflevels = [0,
               5,   #white
              10,     #blue
              15,   #royalblue
              20,    #cyan
              25,   #light green
              30,     #dark green
              50,   #yellow
              75,    #orange
              100,  #tomato red
              125,    #dark red
              150 ]  #magenta

  cfcolors = ['white',
              'blue',
              'royalblue',
              'cyan',
              'lawngreen',
              'green',
              'yellow',
              'orange',
              'red',
              'maroon',
              'magenta']

  cm = matplotlib.colors.ListedColormap(cfcolors)
  norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)  
  
  try:
    cf = ax.contourf(lon, lat, uphl_masked, cflevels, cmap=cm, norm=norm, transform=transform,extend='both')
    cbshrink = 1.0
    cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=cbshrink, extendrect=True, 
               ticks=[0,5,10,15,20,25,30,50,75,100,125,150])
    cb.ax.set_yticklabels(['0','5','10','15','20','25','30','50','75','100','125','150'])

  except:
    print('ax.contourf failed, continue anyway')
  
  ax.plot(lon_adeck[0:frame+2], lat_adeck[0:frame+2], '.-k', markersize=1, linewidth=0.5)
  
  # Add borders and coastlines
  ax.add_feature(cfeature.BORDERS, linewidth=0.5, facecolor='none', edgecolor='gray')
  ax.add_feature(cfeature.STATES, linewidth=0.5, facecolor='none', edgecolor='gray')
  ax.add_feature(cfeature.COASTLINE, linewidth=1.0, facecolor='none', edgecolor='dimgray')
  
  gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.6, color='lightgray', alpha=0.6, linestyle=(0, (5, 10)))
  gl.top_labels = False
  gl.right_labels = False
  gl.xlabel_style = {'size': 8, 'color': 'black'}
  gl.ylabel_style = {'size': 8, 'color': 'black'}
  
  print('lonlat limits: ', [lonmin, lonmax, latmin, latmax])
  ax.set_extent([lonmin, lonmax, latmin, latmax], crs=transform)
  
  title_center = '3 Hour Max. 2-5km Updraft Helicity (m^2/s^2)'
  ax.set_title(title_center, loc='center', y=1.05)
  title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
  ax.set_title(title_left, loc='left')
  
  title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+'F'+conf['fhhh']+conf['validTime'].strftime(' Valid: %Y%m%d%HZ') #+' for ' + str(accumulation_time) + ' h'
  ax.set_title(title_right, loc='right',x=1.05)
  
  fig_name = fig_prefix+'.helicity.2-5km'+'.f'+conf['fhhh']+'.png'
  plt.savefig(fig_name, bbox_inches='tight')
  plt.close(fig)

  if conf['fhhh'] == fhour[len(fhour)-1] :
    print('Stop at',fhour[len(fhour)-1],conf['fhhh'],frame)
    sys.exit()
