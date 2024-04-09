#!/usr/bin/env python3

"""This script is to plot out HAFS atmospheric South-North cross section from 1000-100mb at model's storm center (ATCF)."""

import os

import yaml
import numpy as np
import pandas as pd

import grib2io

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy

import metpy
import metpy.calc as mpcalc

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

#for tt in np.arange(0,127,3):
for tind in tmp1:
  if df.loc[tind][5] == conf['fhour']:
    print(tind)
    break

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
fcor=metpy.calc.coriolis_parameter(np.deg2rad(lat))

print('extract levs='+str(grblevs))
for ind, lv in enumerate(grblevs):
  levstr= str(lv)+' mb'
  print('Extracting data at '+levstr)
  rh = grb.select(shortName='RH', level=levstr)[0].data
  if ind == 0:
    rhtmp=np.zeros((len(grblevs),rh.shape[0],rh.shape[1]))
    rhtmp[ind,:,:]=rh
  rhtmp[ind,:,:]=rh

  ugrd = grb.select(shortName='UGRD', level=levstr)[0].data
  ugrd = ugrd*1.94384
  if ind == 0:
    ugrdtmp=np.zeros((len(grblevs),ugrd.shape[0],ugrd.shape[1]))
    ugrdtmp[ind,:,:]=ugrd
  ugrdtmp[ind,:,:]=ugrd
  
  vgrd = grb.select(shortName='VGRD', level=levstr)[0].data
  vgrd = vgrd*1.94384
  if ind == 0:
    vgrdtmp=np.zeros((len(grblevs),vgrd.shape[0],vgrd.shape[1]))
    vgrdtmp[ind,:,:]=vgrd
  vgrdtmp[ind,:,:]=vgrd

  absvor = grb.select(shortName='ABSV', level=levstr)[0].data
  if ind == 0:
    vorttmp=np.zeros((len(grblevs),absvor.shape[0],absvor.shape[1]))
    vorttmp[ind,:,:]=absvor-np.asarray(fcor)
  vorttmp[ind,:,:]=absvor-np.asarray(fcor)

  tmp = grb.select(shortName='TMP', level=levstr)[0].data
  if ind == 0:
    tmp_anomaly=np.zeros((len(grblevs),tmp.shape[0],tmp.shape[1]))
  tmp_mean = np.nanmean(tmp)
  tmp_anomaly[ind,:,:] = tmp - tmp_mean

########    PLOTTING SETTING
idx = find_nearest(clon, clat, lon, lat)

print(idx[0],idx[1])
fig, (ax2) = plt.subplots(nrows=1, ncols=1,figsize=(10,5))

fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']
fig_name = fig_prefix+'.storm.'+'crs_sn_rh_tempanomaly_wind_rvor.'+conf['fhhh'].lower()+'.png'
cbshrink = 1.0
lonmin = lon[int(nlat/2), int(nlon/2)]-3
lonmax = lon[int(nlat/2), int(nlon/2)]+3
latmin = lat[int(nlat/2), int(nlon/2)]-3
latmax = lat[int(nlat/2), int(nlon/2)]+3
skip = 20
wblength = 5

cflevels = [0,5,10,15,20,25,30,         # TD
            35,40,45,50,55,60,          # TS
            65,70,75,80,                # H1
            85,90,95,                   # H2
            100,105,110,115,            # H3
            120,125,130,135,            # H4
            140,145,150,155,160,165]    # H5

cfcolors = ['white','white','#e0ffff','#80ffff','#00e0e0','#00c0c0','#00a0a0',                # TD: Cyan
            '#a0ffa0','#00ff00','#00e000','#00c000','#00a000','#008000',                      # TS: Green
            '#ffff80','#e0e000','#c0c000','#a0a000',                                          # H1: Yellow
            '#ffc000','#ffa000','#ff8000',                                                    # H2: Orange
            '#ff8080','#ff6060','#ff4040','#ff0000',                                          # H3: Red
            '#e00000','#c00000','#a00000','#800000',                                          # H4: Darkred
            '#ffa0ff','#ff60ff','#ff00ff','#c000c0','#a000a0','#800080']                      # H5: Magenta

cm = matplotlib.colors.ListedColormap(cfcolors)

vmax=np.zeros((len(grblevs),vgrd.shape[0],vgrd.shape[1]))
vmax=(ugrdtmp**2+vgrdtmp**2)**0.5

idx = find_nearest(clon, clat, lon, lat)

######### RH vort Ta wind plot
cflevels = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,99]
cfcolors = ['#996515','#a3742c','#ad8444','#b8935b','#c2a373','#ccb28a','#d6c1a1','#e0d1b9','#ebe0d0','#f5f0e8', # Brown https://colorswall.com/palette/26287
            '#ffffff','#d1e6cf','#bbdab7','#a4ce9f','#8dc287','#76b56e','#5fa956','#499d3e','#329026','#1b840e','#008000'] # Green https://colorswall.com/palette/1386
newlats, levs = np.meshgrid(lat[100:700, idx[1]], grblevs)

cs2 = ax2.contourf(newlats, levs, ( rhtmp[:, 100:700 , idx[1]] ), colors=cfcolors, levels=cflevels, extend='max')
cb2 = plt.colorbar(cs2, ax=ax2, orientation='vertical', pad=0.02, aspect=50, extendfrac='auto', shrink=cbshrink, extendrect=True, ticks=cflevels)

##############Modify axis tick label
plt.savefig('for_axis_tmp', bbox_inches='tight')
locs=ax2.get_xticks()
labels = ax2.get_xticklabels()
latlab=[]
for j in range(len(labels)):
  str1=str(labels[j])
  for i in str1.split():
    if i.startswith("Text(") :
      lattmp=float(i.strip('Text(,'))

      if lattmp > 0:
        str2=str(lattmp)+'N'
      else :
        str2=str(lattmp)+'S'
        str2=str2.strip('-')
      latlab.append(str2)

ax2.set_xticks(locs)
ax2.set_xticklabels(latlab)
#####################

zerowind=np.zeros(newlats.shape)
wb2 = ax2.barbs(newlats[::2,::20], levs[::2,::20], vgrdtmp[::2, 100:700:20 , idx[1]],  zerowind[::2, ::20],length=wblength, linewidth=0.25, color='black') 

if np.max(tmp_anomaly[:,100:700, idx[1]]) > 4:
  cflevels = np.arange(4,17,2)
  cf2 = ax2.contour(newlats, levs, ( tmp_anomaly[:, 100:700 , idx[1]] ), cflevels, colors='red', linestyles='dotted')
  plt.clabel(cf2, cflevels, fontsize=10)

if np.max(vorttmp[:, 100:700 , idx[1]]*10**5) > 30:
  cflevels = [50,100,150]
  cf3 = ax2.contour(newlats, levs, ( vorttmp[:, 100:700 , idx[1]]*10**5 ), cflevels, colors='black')
  plt.clabel(cf3, cflevels, fontsize=10)

ax2.set_yscale('log')
ax2.set_ylim(1000,100)
ax2.set_yticks(range(1000, 99, -100))
ax2.set_yticklabels(range(1000, 99, -100))

if clon > 180.:
  clonpr=str(round( (clon-360.),2) ).strip('-')+'W'
else:
  clonpr=str(round(clon,2))+'E'

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'RH(%), Temperature anomaly(C), Relative vorticity (x 10^-5/s), Meridional Wind (kts) cross section at '+str(clonpr)
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}
{1}
{2}""".format(model_info,var_info,storm_info)
ax2.set_title(title_left, loc='left', y=0.99)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax2.set_title(title_right, loc='right', y=0.99)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax2.text(1.0,-0.13, footer, fontsize=12, va="top", ha="right", transform=ax2.transAxes)

plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
os.remove('for_axis_tmp.png')

