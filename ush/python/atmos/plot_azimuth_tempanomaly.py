#!/usr/bin/env python3

""" This script is to plot out HAFS atmospheric azimuthally averaged fields figures."""
import os

import yaml
import numpy as np
import pandas as pd
from scipy import interpolate

import grib2io

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

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

# Input parameters for this script
resolution=0.02*111     # 0.02 is the resolution of MOVING NEST GRIB2 data
rmax=400.0              # Range of radius (km) that will be plotted
xsize=1001              # X-dim size of MOVING NEST GRIB2 data
ysize=801               # Y-dim size of MOVING NEST GRIB2 data
zsize=45                # Z-dim size (pressure level) of MOVING NEST GRIB2 data
levs=[1000, 975, 950, 925, 900, 875, 850, 825, 800, 775, 750, 725, 700, 675, 650, 625, 600, 575, 550, 525, 500, 475,
         450, 425, 400, 375, 350, 325, 300, 275, 250, 225, 200, 175, 150, 125, 100, 70, 50, 30, 20, 10, 7, 5, 2]

print('Parse the config file: plot_atmos.yml:')
with open('plot_atmos.yml', 'rt') as f:
    conf = yaml.safe_load(f)
conf['stormNumber'] = conf['stormID'][0:2]
conf['initTime'] = pd.to_datetime(conf['ymdh'], format='%Y%m%d%H', errors='coerce')
conf['fhour'] = int(conf['fhhh'][1:])
conf['fcstTime'] = pd.to_timedelta(conf['fhour'], unit='h')
conf['validTime'] = conf['initTime'] + conf['fcstTime']
fhour= int(conf['fhhh'][1:])

# Read ATCF track file to find the TC center at certain forecast hour
atcftrack = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.trak.atcfunix'
trackfile = os.path.join(conf['COMhafs'], atcftrack)
track=open(trackfile,'r')
print('ATCF track file',atcftrack)
tracklist=track.readlines()
cen_lon=[]
cen_lat=[]
for i in range(len(tracklist)):
    tracklist[i]=tracklist[i].strip()
    data=tracklist[i].split(',')
    if int(data[5]) == int(fhour):
        latc=data[6]
        lonc=data[7]
        cen_lat=int(latc[:-1])/10
        cen_lon=int(lonc[:-1])/10
        if lonc[-1] == "W":
            cen_lon=-1.0*cen_lon
        if latc[-1] == "S":
            cen_lat=-1.0*cen_lat

if not cen_lon or not cen_lat:
    print('WARNING: No ATCF track record found at F',fhour)
    print('Exiting ...')
    sys.exit()
else:
    print('TC center at F',fhour,' is',cen_lat,cen_lon)

# Initialization of arrays by setting them as 0
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

# Read variables from GRIB2 file
fname = conf['stormID'].lower()+'.'+conf['ymdh']+'.'+conf['stormModel'].lower()+'.'+conf['stormDomain']+'.atm.'+conf['fhhh']+'.grb2'
grib2file = os.path.join(conf['COMhafs'], fname)
print(f'grib2file: {grib2file}')
grb = grib2io.open(grib2file,mode='r')

print('Extracting NLAT')
lat = grb.select(shortName='NLAT')[0].data
lat = np.asarray(lat[::-1,:])
for i in range(ysize):
    for j in range(xsize):
        latp[(ysize-1)-i]=lat[i,j]

print('Extracting ELON')
lon = grb.select(shortName='ELON')[0].data
lon = np.asarray(lon[::-1,:])
for i in range(ysize):
    for j in range(xsize):
        if lonc[-1] == "W":
            lonp[j]=lon[i,j]-360.0
        if lonc[-1] == "E":
            lonp[j]=lon[i,j]

# Put variables into 3-d array, index i is for y-dim, index j is for x-dim
for k in range(zsize):
    levstr = str(levs[k])+' mb'
    tmp = grb.select(shortName='TMP', level=levstr)[0].data
    print('Reading TMP for level',k,levs[k])
    for i in range(ysize):
        for j in range(xsize):
            tprs[i,j,k]=tmp[i,j]
    print('Calculating T anomaly for level',k,levs[k])
    tmp_mean = np.nanmean(tmp)
    tmp_anomaly = tmp - tmp_mean
    tmp_anomaly = np.asarray(tmp_anomaly)
    for i in range(ysize):
        for j in range(xsize):
            tano[i,j,k]=tmp_anomaly[i,j]

# Get pressure levels
zlevs = levs[:]
z = np.zeros((zsize,0))*np.nan
for i in range(zsize): z[i] = levs[i]

# Get storm-centered data
lon_sr = lonp-cen_lon
lat_sr = latp-cen_lat
x_sr = lon_sr*111.1e3*np.cos(cen_lat*3.14159/180)   # degree to meter
y_sr = lat_sr*111.1e3                               # degree to meter

# Define the polar coordinates needed
r = np.linspace(0,rmax,(int(rmax//resolution)+1))
pi = np.arccos(-1)
theta = np.arange(0,2*pi+pi/36,pi/36)
R, THETA = np.meshgrid(r, theta)
XI = R * np.cos(THETA)
YI = R * np.sin(THETA)

# Convert meter to km
x_sr = np.round(x_sr/1000,3)
y_sr = np.round(y_sr/1000,3)
x_sr_2 = np.linspace(x_sr.min(), x_sr.max(), x_sr.size)
y_sr_2 = np.linspace(y_sr.min(), y_sr.max(), y_sr.size)

# Do interpolation
print('MSG: Doing the Polar Interpolation Now')
t_p = np.ones((np.shape(XI)[0],np.shape(XI)[1],zsize))*np.nan
tano_p = np.ones((np.shape(XI)[0],np.shape(XI)[1],zsize))*np.nan
for k in range(zsize):
    f_t = interpolate.RegularGridInterpolator((y_sr, x_sr), tprs[:,:,k])
    f_tano = interpolate.RegularGridInterpolator((y_sr, x_sr), tano[:,:,k])
    t_p[:,:,k] = f_t((YI,XI),method='linear')
    tano_p[:,:,k] = f_tano((YI,XI),method='linear')
# Calculate azimuthal means
t_p_mean = np.nanmean(t_p,0)
tano_p_mean = np.nanmean(tano_p,0)

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
mpl.rcParams['legend.fontsize'] = 8

# Create figure and axes instances
fig = plt.figure(figsize=(8.0, 4.0))
ax = fig.add_subplot(1, 1, 1)

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

cm = mpl.colors.ListedColormap(cfcolors)
norm = mpl.colors.BoundaryNorm(cflevels, cm.N)
cf = ax.contourf(r, zlevs, np.flipud(np.rot90(tano_p_mean,5)), cflevels, cmap=cm, norm=norm, extend='max')
cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=50, shrink=1.0, extendrect=True,
                  ticks=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
cb.ax.set_yticklabels(['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'])

cs = ax.contour(r, zlevs, np.flipud(np.rot90(t_p_mean,1)), np.arange(200,500,5), colors='black', linewidths=0.6)
lb = plt.clabel(cs, levels=np.arange(200,500,10), inline_spacing=1, fmt='%d', fontsize=9)
ax = axes_radpres(ax, rmax, 0)

model_info = os.environ.get('TITLEgraph','').strip()
var_info = 'Temperature (K), Temperature Anomaly (K, shaded)'
storm_info = conf['stormName']+conf['stormID']
title_left = """{0}
{1}
{2}""".format(model_info,var_info,storm_info)
ax.set_title(title_left, loc='left', y=0.99)
title_right = conf['initTime'].strftime('Init: %Y%m%d%HZ ')+conf['fhhh'].upper()+conf['validTime'].strftime(' Valid: %Y%m%d%HZ')
ax.set_title(title_right, loc='right', y=0.99)
footer = os.environ.get('FOOTERgraph','Experimental HAFS Product').strip()
ax.text(1.0,-0.15, footer, fontsize=10, va="top", ha="right", transform=ax.transAxes)

#plt.show()
plt.savefig(fig_name, bbox_inches='tight')
plt.close(fig)
