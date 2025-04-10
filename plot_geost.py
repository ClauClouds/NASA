"""
Routine to plot geostationary data and imerg data on the same date 
and time

"""

import os
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from matplotlib.colors import BoundaryNorm
from matplotlib import colors
from matplotlib import cm
from datetime import datetime, timedelta
from matplotlib import ticker
from matplotlib import gridspec
from matplotlib import colorbar
from matplotlib import rcParams
from matplotlib import rc
import glob
from cftime import DatetimeJulian


def main():
    
    url_itcz = '/data/trade_pc/ITCZ/2024'
    path_geost = url_itcz+'/geost/'
    path_imerg = url_itcz+'/imerg/'
    
    # define date and time for plot
    day = '2024-01-14'
    hh = '18'
    min = '00'
    sec = '00'
    
    yy = day.split('-')[0]
    mm = day.split('-')[1]
    dd = day.split('-')[2]
    
    # create the date and time string
    date_time_str = f"{day} {hh}:{min}:{sec}"
    # convert to datetime object
    dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    
    # convert dt in datetime64 
    dt_64 = np.datetime64(dt)
    
    # Create a compatible datetime object
    #dt_cftime = nc4.num2date(date_time_str, units='hours since 1970-01-01', only_use_cftime_datetimes=True, only_use_python_datetimes=False)
    
    # read files 
    file_imerg = path_imerg + day + '_imerg_30min_ITCZ.nc'
    
    print(path_geost + 'GRIDSAT-B1.' + yy + '.'+ mm+'.'+dd+'.*')
    filelist_geost = sorted(glob.glob(path_geost + 'GRIDSAT-B1.' + yy + '.'+ mm+'.'+dd+'.*'))
        
    # read geostationary data
    ds_geost = xr.open_mfdataset(filelist_geost, drop_variables=['sparse3ir', 'irwvp_2', 'b1file'])
    ds_geost = ds_geost.convert_calendar('standard', align_on='year')
    

    # read imerg data
    ds_imerg = xr.open_dataset(file_imerg)
    ds_imerg = ds_imerg.convert_calendar('standard', align_on='year')
    
    # select the time stamp
    ds_geost_sel = ds_geost.sel(time=dt_64, method='nearest')
    ds_imerg_sel = ds_imerg.sel(time=dt_64, method='nearest')
    
    print(dt)
    print(ds_geost_sel.time.values)    
    print(ds_imerg_sel.time.values)  
    
     
    # create the figure
    # Get the precipitation, latitude, and longitude variables
    precip = ds_imerg_sel['precipitation'][:,:].values
    precip = np.transpose(precip)
    theLats = ds_imerg_sel['lat'].values
    theLons = ds_imerg_sel['lon'].values
    x, y = np.float32(np.meshgrid(theLons, theLats))
    
    # get the brightness temperature, latitude, and longitude variables
    bt11 = ds_geost_sel['irwin_cdr'][:,:].values
    #bt11 = np.transpose(bt11)
    latsBT = ds_geost_sel['lat'].values
    lonsBT = ds_geost_sel['lon'].values
    x1, y1 = np.float32(np.meshgrid(lonsBT, latsBT))
    # Create a meshgrid with one extra row and column
    x1_edges = np.linspace(x1.min(), x1.max(), bt11.shape[1] + 1)
    y1_edges = np.linspace(y1.min(), y1.max(), bt11.shape[0] + 1)
    X1, Y1 = np.meshgrid(x1_edges, y1_edges)

    # find max and min of BT
    bt_min = np.nanmin(bt11)
    bt_max = np.nanmax(bt11)
    
       
    # define ITCZ domain
    lat_min = -15
    lat_max = 15
    lon_min = -66
    lon_max = 15

    
    fig = plt.figure(figsize=(12, 8))
    ax1 = plt.axes(projection=ccrs.PlateCarree())
    ax1.set_title('Geostationary data')
    ax1.set_extent([lon_min, lon_max, lat_min, lat_max])
    ax1.coastlines(resolution="110m", linewidth=1)
    gl1 = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=1, color='black', linestyle='--')
    gl1.xlabels_top = False
    gl1.ylabels_right = False
    gl1.xlines = True
    gl1.xlocator = mticker.FixedLocator([-60, -45, -30, -15, 0, 15])
    gl1.ylocator = mticker.FixedLocator([-15, -10, -5, 0, 5, 10, 15])
    gl1.xformatter = LONGITUDE_FORMATTER
    gl1.yformatter = LATITUDE_FORMATTER
    gl1.xlabel_style = {'size': 16, 'color': 'black'}
    gl1.ylabel_style = {'size': 16, 'color': 'black'}
    
    # Set contour levels
    clevs1 = np.arange(bt_min, bt_max, 5.)

    # Normalize the data to match clevs
    norm1 = BoundaryNorm(clevs1,
                        ncolors=plt.cm.grey_r.N, 
                        clip=True)

    # Plot the data with pcolormesh
    mesh1 = plt.pcolormesh(X1, 
                          Y1, 
                          bt11, 
                          cmap=plt.cm.grey_r, 
                          norm=norm1, 
                          shading='flat')

    # Add a colorbar
    cb1 = plt.colorbar(mesh1, 
                      ax=ax1, 
                      orientation="vertical", 
                      pad=0.05, 
                      aspect=16, 
                      shrink=0.8)
    
    cb1.set_label('Kelvin', size=20)
    cb1.ax.tick_params(labelsize=16)
    # save figure
    plt.savefig('/net/ostro/ITCZ/plots/'+date_time_str+'_geost.png', 
                dpi=300, 
                transparent=True,
                bbox_inches='tight')
    
    
    
    fig = plt.figure(figsize=(12, 8))
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    ax2.set_title('IMERG data')
    ax2.set_extent([lon_min, lon_max, lat_min, lat_max])
    ax2.coastlines(resolution="110m", linewidth=1)
    gl = ax2.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=1, color='black', linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xlines = True
    gl.xlocator = mticker.FixedLocator([-60, -45, -30, -15, 0, 15])
    gl.ylocator = mticker.FixedLocator([-15, -10, -5, 0, 5, 10, 15])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 16, 'color': 'black'}
    gl.ylabel_style = {'size': 16, 'color': 'black'}

    # Set contour levels
    clevs = np.arange(0, 3, 0.05)

    # Normalize the data to match clevs
    norm = BoundaryNorm(clevs,
                        ncolors=plt.cm.rainbow.N, 
                        clip=True)

    # Plot the data with pcolormesh
    mesh = plt.pcolormesh(x, 
                          y, 
                          precip, 
                          cmap=plt.cm.rainbow, 
                          norm=norm, 
                          shading="auto")

    # Add a colorbar
    cb = plt.colorbar(mesh, 
                      ax=ax2, 
                      orientation="vertical", 
                      pad=0.05, 
                      aspect=16, 
                      shrink=0.8)
    
    cb.set_label('mm / hr', size=20)
    cb.ax.tick_params(labelsize=16)

    # save figure
    plt.savefig('/net/ostro/ITCZ/plots/'+date_time_str+'_imerg.png', 
                dpi=300, 
                transparent=True,
                bbox_inches='tight')
    

if __name__ == "__main__":
    main()
    
    