"""

 plot_storm_mld.py
 -------------
    read a HYCOM 3z .nc file,
    extract footprint MLD and plot in time series (R<=500km)


 ************************************************************************
 usage: python plot_storm_mld.py stormModel stormName stormID YMDH trackon COMhafs graphdir
 -----
 ************************************************************************


 HISTORY
 -------
    modified to implement new filenames and hycom domains, as well as
        improve graphics -JS & MA 06/2022
    modified to comply the convention of number of input argument and 
       graphic filename. -hsk 8/2020
    modified to take global varibles from kick_graphics.py -hsk 9/20/2018
    modified to fit for RT run by Hyun-Sook Kim 5/17/2017
    edited by Hyun-Sook Kim 9/18/2015
    modified by Hyun-Sook Kim 11/18/2016
---------------------------------------------------------------
"""

from utils4HWRF import readTrack6hrly
from geo4HYCOM import haversine

import os
import sys
import glob
import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

plt.switch_backend('agg')

#================================================================
model = sys.argv[1]
storm = sys.argv[2]
tcid = sys.argv[3]
cycle = sys.argv[4]
trackon = sys.argv[5]
COMOUT = sys.argv[6]
graphdir = sys.argv[7]

#model = 'hfsa'
#storm = 'DOKSURI'
#tcid = '05w'
#cycle = '2023072118'
#trackon = 'yes'
#COMOUT = '/lfs/h1/ops/prod/com/hafs/v1.0/hfsa.20230721/18'
#graphdir = './'

#model = 'hfsa'
#storm = 'CALVIN'
#tcid = '03e'
#cycle = '2023071906'
#trackon = 'yes'
#COMOUT = '/lfs/h1/ops/prod/com/hafs/v1.0/hfsa.20230719/06'
#graphdir = './'

#model = 'hfsa'
#storm = 'DON'
#tcid = '05l'
#cycle = '2023072318'
#trackon = 'yes'
#COMOUT = '/lfs/h1/ops/prod/com/hafs/v1.0/hfsa.20230723/18'
#graphdir = './'

if not os.path.isdir(graphdir):
      p=Path(graphdir)
      p.mkdir(parents=True)

print("code:   plot_storm_mld.py")

atcf = COMOUT+'/' + tcid + '.' + cycle + '.' + model + '.trak.atcfunix'

adt,aln,alt,pmn,vmx = readTrack6hrly(atcf)

# Set Cartopy data_dir location
cartopy.config['data_dir'] = os.getenv('cartopyDataDir')

#   ------------------------------------------------------------------------------------
Rkm=500    # search radius [km]

# - get SST  *_3z_*.[nc] files
afiles = sorted(glob.glob(os.path.join(COMOUT,tcid+'*3z*.nc')))

ncfile0 = xr.open_dataset(afiles[0])

var0 = ncfile0['mixed_layer_thickness'][0,:,:]
lon = np.asarray(ncfile0.Longitude)
lat = np.asarray(ncfile0.Latitude)
lonmin_raw = np.min(lon)
lonmax_raw = np.max(lon)
print('raw lonlat limit: ', np.min(lon), np.max(lon), np.min(lat), np.max(lat))

# Constrain lon limits between -180 and 180 so it does not conflict with the cartopy projection PlateCarree
lon[lon>180] = lon[lon>180] - 360
sort_lon = np.argsort(lon)
lon = lon[sort_lon]

# Sort var0 according to new longitude
var0 = var0[:,sort_lon]

# define grid boundaries
lonmin_new = np.min(lon)
lonmax_new = np.max(lon)
latmin = np.min(lat)
latmax = np.max(lat)
print('new lonlat limit: ', lonmin_new, lonmax_new, latmin, latmax)

# Set new longitude track (aln) according with the ocean domain limits following the -180 to 180 convenction
aln[np.logical_or(aln<lonmin_new,aln>lonmax_new)] = np.nan

var_name = 'mld'
units = '(m)'

# Shift central longitude so the Southern Hemisphere and North Indin Ocean domains are plotted continuously
if np.logical_and(lonmax_new >= 90, lonmax_new <=180):
    central_longitude = 90
else:
    central_longitude = -90
print('central longitude: ',central_longitude)

lns,lts = np.meshgrid(lon,lat)
dummy = np.ones(lns.shape)

count = len(aln[np.isfinite(aln)])        
for k in range(count):

    if alt[k] < (np.max(lat)+5.0):
        dR=haversine(lns,lts,aln[k],alt[k])/1000.
        dumb=dummy.copy()
        dumb[dR>Rkm]=np.nan
         
        ncfile = xr.open_dataset(afiles[k])

        varr = ncfile['mixed_layer_thickness']
        # Sort varr according to new longitude
        varr = np.asarray(varr[0,:,sort_lon])
        var = varr*dumb
        
        dvar = np.asarray(var - var0)*dumb

        # define forecast hour
        fhr=k*6
        
        # create figure and axes instances
        fig = plt.figure(figsize=(6,6))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=central_longitude))
        ax.axis('scaled')
        
        cflevels = np.linspace(0, 100, 21)
        cmap = plt.get_cmap('RdYlBu_r')
        cf = ax.contourf(lon, lat, var, levels=cflevels, cmap=cmap, extend='max', transform=ccrs.PlateCarree())
        ax.contour(lon, lat, var, cflevels, colors='grey',alpha=0.5, transform=ccrs.PlateCarree())
        cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=30, shrink=0.75, extendrect=True, ticks=cflevels[::4])
        cb.ax.tick_params(labelsize=8)

        if trackon[0].lower()=='y':
              plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2,transform=ccrs.PlateCarree(central_longitude=0))
              plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6,transform=ccrs.PlateCarree(central_longitude=0))

        mnmx="(min,max)="+"(%6.1f"%np.nanmin(var)+","+"%6.1f)"%np.nanmax(var)

        if np.logical_and(aln[k]-5.5 > lonmin_new,aln[k]+5.5 < lonmax_new): 
            plt.text(aln[k]-2.15-central_longitude,alt[k]-4.75,mnmx,fontsize=8,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5))
            ax.set_extent([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5],crs=ccrs.PlateCarree())
        else:
            print('Longitude track limits are out of the ocean domain')
            continue
     
        # Add gridlines and labels
        #gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
        gl.top_labels = False
        gl.right_labels = False
        gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, 2))
        gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, 2))
        gl.xlabel_style = {'size': 8, 'color': 'black'}
        gl.ylabel_style = {'size': 8, 'color': 'black'}
        
        # Add borders and coastlines
        #ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
     
        title_center = 'Mixed Layer Depth (m)'
        ax.set_title(title_center, loc='center', y=1.05, fontsize=8)
        title_left = model.upper()+' '+storm.upper()+tcid.upper()
        ax.set_title(title_left, loc='left', fontsize=8)
        title_right = 'Init: '+cycle+'Z '+'F'+"%03d"%(fhr)
        ax.set_title(title_right, loc='right', fontsize=8)
      
        pngFile=os.path.join(graphdir,storm.upper()+tcid.upper()+'.'+cycle+'.'+model.upper()+'.ocean.storm.'+var_name+'.f'+"%03d"%(fhr)+'.png')
        plt.savefig(pngFile,bbox_inches='tight',dpi=150)
        plt.close("all")
     
        # create figure and axes instances for change plot
        fig = plt.figure(figsize=(6,6))
        ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=central_longitude))
        ax.axis('scaled')
     
        cflevels = np.linspace(-30, 30, 31)
        cmap = plt.get_cmap('RdBu_r')
        cf = ax.contourf(lon, lat, dvar, levels=cflevels, cmap=cmap, extend='both', transform=ccrs.PlateCarree())
        ax.contour(lon, lat, dvar, cflevels[::2], colors='grey',alpha=0.5, transform=ccrs.PlateCarree())
        cb = plt.colorbar(cf, orientation='vertical', pad=0.02, aspect=30, shrink=0.75, extendrect=True, ticks=cflevels[::5])
        cb.ax.tick_params(labelsize=8)

        if trackon[0].lower()=='y':
              plt.plot(aln,alt,'-ok',linewidth=3,alpha=0.6,markersize=2,transform=ccrs.PlateCarree(central_longitude=0))
              plt.plot(aln[k],alt[k],'ok',markerfacecolor='none',markersize=10,alpha=0.6,transform=ccrs.PlateCarree(central_longitude=0))

        mnmx="(min,max)="+"(%6.1f"%np.nanmin(dvar)+","+"%6.1f)"%np.nanmax(dvar)

        if np.logical_and(aln[k]-5.5 > lonmin_new,aln[k]+5.5 < lonmax_new):
            plt.text(aln[k]-2.15-central_longitude,alt[k]-4.75,mnmx,fontsize=8,color='DarkOliveGreen',fontweight='bold',bbox=dict(boxstyle="round",color='w',alpha=0.5)) 
            ax.set_extent([aln[k]-5.5,aln[k]+5.5,alt[k]-5,alt[k]+5],crs=ccrs.PlateCarree())
        else:            
            print('Longitude track limits are out of the ocean domain')
            continue
     
        # Add gridlines and labels
        #gl = ax.gridlines(crs=transform, draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.1', alpha=0.6, linestyle=(0, (5, 10)))
        gl.top_labels = False
        gl.right_labels = False
        gl.xlocator = mticker.FixedLocator(np.arange(-180., 180.+1, 2))
        gl.ylocator = mticker.FixedLocator(np.arange(-90., 90.+1, 2))
        gl.xlabel_style = {'size': 8, 'color': 'black'}
        gl.ylabel_style = {'size': 8, 'color': 'black'}
     
        # Add borders and coastlines
        #ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='whitesmoke')
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
        ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.3, facecolor='none', edgecolor='0.1')
     
        title_center = 'Mixed Layer Depth Change (m)'
        ax.set_title(title_center, loc='center', y=1.05, fontsize=8)
        title_left = model.upper()+' '+storm.upper()+tcid.upper()
        ax.set_title(title_left, loc='left', fontsize=8)
        title_right = 'Init: '+cycle+'Z '+'F'+"%03d"%(fhr)
        ax.set_title(title_right, loc='right', fontsize=8)
     
        pngFile=os.path.join(graphdir,storm.upper()+tcid.upper()+'.'+cycle+'.'+model.upper()+'.ocean.storm.'+var_name+'.change.f'+"%03d"%(fhr)+'.png')
        plt.savefig(pngFile,bbox_inches='tight',dpi=150)
        plt.close("all")

# --- successful exit
#sys.exit(0)

