#!/usr/bin/env python3

""" This script is to plot out HAFS atmospheric azimuthally averaged fields figures."""
import os
import sys
import logging
import math
import datetime

import yaml
import numpy as np
import pandas as pd
from numpy import newaxis
from scipy.ndimage import gaussian_filter
import matplotlib.colors as colors #Command to do some colorbar stuff
from scipy import interpolate #The interpolation function

import grib2io

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

###############################################################################
def axes_radpres(ax, xmax, xmin, ymax=1000, ymin=100):
        """Set up common axes attributes for wavenumber graphics.
        @param ax:    the axes object
        @param axmax: max value of both x/y axes
        @param axmin: min value of both x/y axes
        """
        xticks = np.linspace(xmin,xmax,9)
        yticks = np.linspace(1000,100,10)

        ax.set_xlim(xmin, xmax)
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(int(x)) for x in xticks], fontsize=10)
        ax.set_xlabel('Radius (km)', fontsize=10)

        ax.set_yscale('log')
        ax.set_ylim(ymin,ymax)
        ax.invert_yaxis()
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(int(x)) for x in yticks], fontsize=10)
        ax.set_ylabel('Pressure (hPa)', fontsize=10)

        ax.grid(linestyle = "dashed")

        return ax
###############################################################
##################################################################
#-------------------------------------------------------------------------------
# Section 1. Input parameters for this script

resolution=0.02*111     # 0.02 is the resolution of MOVING NEST GRIB2 data
rmax=400.0              # Range of radius (km) that will be plotted
xsize=1001              # X-dim size of MOVING NEST GRIB2 data 
ysize=801               # Y-dim size of MOVING NEST GRIB2 data
zsize=45                # Z-dim size (pressure level) of MOVING NEST GRIB2 data
levs=[1000, 975, 950, 925, 900, 875, 850, 825, 800, 775, 750, 725, 700, 675, 650, 625, 600, 575, 550, 525, 500, 475,
         450, 425, 400, 375, 350, 325, 300, 275, 250, 225, 200, 175, 150, 125, 100, 70, 50, 30, 20, 10, 7, 5, 2]

#################################################################################
# Section 2. Read variables from GRIB2 file

#------------------------ Parse the yaml config file ---------------------
print('Parse the config file: plot_atmos.yml:')
with open('plot_atmos.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']
fhour= int(conf['fhhh'][1:])

fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.atm.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

#-------------------------------------------------------------------------
#################################################################################
# Section 3. Read ATCF track file to find the TC center at certain forecast hour
atcftrack = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
trackfile = os.path.join(conf['COMhafs'], atcftrack)
track=open(trackfile,'r')
print('ATCF track file',atcftrack)

tracklist=track.readlines()
for i in range(len(tracklist)):    # Read each line of the ATCF track file
 tracklist[i]=tracklist[i].strip() # Seperate by line
 data=tracklist[i].split(',')      # Remove comma from each line

 if int(data[5]) == int(fhour):    # Extract the line for certain forecast leadtime (fhour)
  latc=data[6]                      # center latitude  e.g., 281N
  lonc=data[7]                      # center longitude e.g., 898W
  cen_lat=int(latc[:-1])/10         # Extract only number from latitude
  cen_lon=int(lonc[:-1])/10         # Extract only number from longitude

  if lonc[-1] == "W":      # This is western hemisphere TC
   cen_lon=-1.0*cen_lon
#   print('western hemisphere')
  if latc[-1] == "S":     # This is southern hemisphere TC
   cen_lat=-1.0*cen_lat
#   print('southern hemisphere')
  print('TC center at F',fhour,' is',cen_lat,cen_lon)

##############################################################################
#===================================================================================================
print('Plotting Azimuthally averaged Temperature & its Anomaly')
fig_prefix = conf['stormName'].upper()+conf['stormID'].upper()+'.'+conf['ymdh']+'.'+conf['stormModel']
fig_name = fig_prefix+'.storm.'+'azimuth_tempanomaly.'+conf['fhhh'].lower()+'.png'

# Set default figure parameters
#mpl.rcParams['figure.figsize'] = [8, 4]
mpl.rcParams["figure.dpi"] = 150
mpl.rcParams['axes.titlesize'] = 8
mpl.rcParams['axes.labelsize'] = 8
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8  #

##############################################################################

# Section 4. Initialization of arrays by setting them as 0
tprs = [[[0.0 for col in range(zsize)] for row in range(xsize)] for depth in range(ysize)]
tano = [[[0.0 for col in range(zsize)] for row in range(xsize)] for depth in range(ysize)]
latp = []  
for i in range(ysize):
 latp.append(0.0)
lonp = []  
for i in range(xsize):
 lonp.append(0.0)

tprs= np.asarray(tprs)
tano= np.asarray(tano)
latp= np.asarray(latp)
lonp= np.asarray(lonp)

#print(np.shape(uwind))       #,np.shape(latp),np.shape(lonp))
#print(uwind[277,277,17])
#------------------------------------------------------------
print('Extracting NLAT')
lat = grb.select(shortName='NLAT')[0].data()
lat=np.asarray(lat[::-1,:])
for i in range(ysize):
 for j in range(xsize):
  latp[(ysize-1)-i]=lat[i,j]

print('Extracting ELON')
lon = grb.select(shortName='ELON')[0].data()
lon=np.asarray(lon[::-1,:])
for i in range(ysize):
 for j in range(xsize):
  if lonc[-1] == "W":
   lonp[j]=lon[i,j]-360.0
  if lonc[-1] == "E":
   lonp[j]=lon[i,j]

#print(np.shape(latp),np.shape(lonp))
#print('lon= ',lonp)
#print('lat= ',latp)
#---------------------------------------------------------------
# put variables into 3-d array, index i is for y-dim, index j is for x-dim
for k in range(zsize):
 levstr=str(levs[k])+' mb'

 tmp = grb.select(shortName='TMP', level=levstr)[0].data()
 tmp.data[tmp.mask] = np.nan
 tmp[tmp<0.] = np.nan
 tmp= np.asarray(tmp)

 for i in range(ysize):
   for j in range(xsize):
    tprs[i,j,k]=tmp[i,j]
 print('Reading TMP for level',k,levs[k])

 tmp_mean = np.nanmean(tmp)
 tmp_anomaly = tmp - tmp_mean
 tmp_anomaly = np.asarray(tmp_anomaly)
 for i in range(ysize):
   for j in range(xsize):
    tano[i,j,k]=tmp_anomaly[i,j]
 print('Calculating t anomaly for level',k,levs[k])

# print(tano[501,401])

#===================================================================================
# Section 5.
######################### The part from HRD script ##################################
# Get pressure levels
zlevs = levs[:]
z = np.zeros((zsize,0))*np.nan
for i in range(zsize):  z[i] = levs[i]

#Get storm-centered data
lon_sr = lonp-cen_lon
lat_sr = latp-cen_lat
x_sr = lon_sr*111.1e3*np.cos(cen_lat*3.14159/180)   # degree in meter
y_sr = lat_sr*111.1e3                               # degree in meter

#Define the polar coordinates needed
r = np.linspace(0,rmax,(int(rmax//resolution)+1))
pi = np.arccos(-1)
theta = np.arange(0,2*pi+pi/36,pi/36)
R, THETA = np.meshgrid(r, theta)
XI = R * np.cos(THETA)
YI = R * np.sin(THETA)

# convert meter to km
x_sr = np.round(x_sr/1000,3)  
y_sr = np.round(y_sr/1000,3)

x_sr_2 = np.linspace(x_sr.min(), x_sr.max(), x_sr.size)
y_sr_2 = np.linspace(y_sr.min(), y_sr.max(), y_sr.size)

# Below print out statements just for checking... 
#print(np.shape(x_sr),np.shape(y_sr))
#print(x_sr)
#print(y_sr)
#print(r) 
#print('XI= ',np.shape(XI))
#print(XI)
#print('YI= ',np.shape(YI))
#print(YI)

#print('(np.shape(XI)[0]= ',np.shape(XI)[0],'(np.shape(XI)[1]= ',np.shape(XI)[1])

#Do interpolation
print('MSG: Doing the Polar Interpolation Now')

#First initialize 
t_p = np.ones((np.shape(XI)[0],np.shape(XI)[1],zsize))*np.nan
tano_p = np.ones((np.shape(XI)[0],np.shape(XI)[1],zsize))*np.nan

for k in range(zsize):
        #print(k) 
        f_t = interpolate.RegularGridInterpolator((y_sr, x_sr), tprs[:,:,k])
        f_tano = interpolate.RegularGridInterpolator((y_sr, x_sr), tano[:,:,k])
        t_p[:,:,k] = f_t((YI,XI),method='linear')
        tano_p[:,:,k] = f_tano((YI,XI),method='linear')

#print('u_p= ',np.shape(u_p))

#Calculate azimuthal means
t_p_mean = np.nanmean(t_p,0)
tano_p_mean = np.nanmean(tano_p,0)

print('Done!')
#print(np.shape(vt_p_mean))
#################### The part from HRD script ##################################
################################################################################
# Section 6. plot

# create figure and axes instances
fig = plt.figure(figsize=(8.0, 4.0))
ax = fig.add_subplot(1, 1, 1)

#cflevels = np.arange(-10,11,1)
#ticks = np.arange(-10,11,1)
#cmap = 'RdBu_r'

#cflevels = [-5,-4,-3,-2,-1,0,                       # cold
#            1,2,3,4,6,8,10,12,14,16]                # warm
#cfcolors = ['#00a0a0','#00c0c0','#00e0e0','#80ffff','#e0ffff','white',          # cold cyan
#            'mistyrose','#ff8080','#ff6060','#ff4040','#ff0000',                # warm Red
#            '#e00000','#c00000','#a00000','#800000']                            # warm Red

cflevels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
cfcolors = ['white',
            '#fbedbc', #Yellow
            '#f9e7a6',
            '#f6dc79',
            '#f2ca36',
            '#feb14c',
            '#fd8d3c',
            '#ef9a9a', #Red
            '#e57373',
            '#ff1744',
            '#d32f2f',
            '#b71c1c',
            '#880e4f', #Pink
            '#c51162',
            '#6a1b9a', #Purple
            '#aa00ff',
            '#d500f9',
            '#ea80fc',
            '#ce93d8']


#cf = ax.contourf(r, zlevs, np.flipud(np.rot90(tano_p_mean,1)), levels=cflevels, cmap=cmap, extend='both')
#cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=1.0, extendrect=True, ticks=ticks)

cm = matplotlib.colors.ListedColormap(cfcolors)
norm = matplotlib.colors.BoundaryNorm(cflevels, cm.N)
cf = ax.contourf(r, zlevs, np.flipud(np.rot90(tano_p_mean,5)), cflevels, cmap=cm, norm=norm, extend='max')
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=1.0, extendrect=True,
                  ticks=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
cb.ax.set_yticklabels(['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])

cs = ax.contour(r, zlevs, np.flipud(np.rot90(t_p_mean,1)), np.arange(200,500,5), colors='black', linewidths=0.6)
lb = plt.clabel(cs, levels=np.arange(200,500,10), inline_spacing=1, fmt='%d', fontsize=9)
ax = axes_radpres(ax, rmax, 0)

#------------------------ set title ----------------------------
title_center = 'Temperature (K), Temperature Anomaly (K, shaded)'
ax.set_title(title_center, loc='center', y=1.05)
title_left = conf['stormModel']+' '+conf['stormName']+conf['stormID']
ax.set_title(title_left, loc='left')
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right')
#---------------------------------------------------------------
#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
###############################################################################
