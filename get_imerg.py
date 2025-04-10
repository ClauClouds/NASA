""" script to download IMERG data from NASA's GPM mission
    using the Earthdata Login API.
    At this link it is possible to download the jupyter notebook to do the same https://disc.gsfc.nasa.gov/information/howto?keywords=Python%20imerg&title=How%20to%20Read%20IMERG%20Data%20Using%20Python
    To make it work one needs to:
    - have valid Earthdata login credentials and have generated the Earthdata pre-requisite files including .netrc and .dodsrc files
    - install on virtual environment the libraries earthaccess, xarray, numpy, matplotlib, cartopy
    
    Other options instead is to get the data with wget or curl, but this is more complicated
    From this link https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary?keywords=IMERG one can do that way
"""
import earthaccess
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from matplotlib.colors import BoundaryNorm
import os
from datetime import datetime, timedelta


def main():

    plotting = 'no'
    # define ITCZ domain
    lat_min = -15
    lat_max = 15
    lon_min = -66
    lon_max = 15

    path_imerg = '/data/trade_pc/ITCZ/2024/imerg'
    domain = [lon_min,lat_min,lon_max, lat_max]
    #domain_all = [-180, 0, 180, 90]
    
    # days for the analysis
    year = 2024
    days = generate_days(year)
    
    for day in days:
        
        print('Processing day:', day)
        
        # check if the file already exists
        file_name = path_imerg + '/' + day + '_imerg_30min_ITCZ.nc'
        if os.path.exists(file_name):
            print('File already exists:', file_name)
            continue
        
        # search files
        start = day
        end = day
        results = auth_and_search(start, end)
        
        # download files for the given day 
        downloaded_files = download_imerg_granule(results, path_imerg)
        
        # read and crop the dataset and merge in one dataset
        ds = read_and_crop_dataset(downloaded_files, lat_min, lat_max, lon_min, lon_max)

        if plotting == 'yes':
            # plot the data for first time stamp
            plot_test_imerg(ds, lat_min, lat_max, lon_min, lon_max)
        
        # store to ncdf
        ds.to_netcdf(path_imerg + '/'+ start + '_imerg_30min_ITCZ.nc', mode='w')
        
        # delete the downloaded files
        for file in downloaded_files:
            print('Deleting file:', file)
            os.remove(file)
    print('All files processed and deleted.')

def generate_days(year=2024):
    """
    Generates an array of strings representing all days in 2024.
    input:
        year (int): The year for which to generate the dates.
    Returns:
        list: A list of date strings in the format 'YYYY-MM-DD'.
    """
    start_date = datetime(2024, 1, 1)  # Start of 2024
    end_date = datetime(2024, 12, 31)  # End of 2024

    # Generate all days in 2024
    days = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
    return days

         
def auth_and_search(start, end):
    """
    Authenticate with Earthdata Login servers and search for granules.
    input:
        start (str): Start date in YYYY-MM-DD format.
        end (str): End date in YYYY-MM-DD format.
    output:
        results (list): List of granule metadata.
    """
    # Authenticate with Earthdata Login servers
    auth = earthaccess.login()

    # Search for granules
    results = earthaccess.search_data(
        short_name="GPM_3IMERGHH",
        version="07",
        temporal=(start, end),
        bounding_box=(-180, 0, 180, 90)
    )

    # Print search results
    print(results)
    return results

def download_imerg_granule(results, path_imerg_data):
    """
    Download IMERG granules to the current working directory.
    input:
        results (list): List of granule metadata.
    output:
        downloaded_files (list): List of downloaded file paths.
    """
    # Download the granule to the current working directory
    downloaded_files = earthaccess.download(
        results,
        local_path=path_imerg_data, # Change this string to download to a different path
    )

    return downloaded_files

def read_and_crop_dataset(downloaded_files, lat_min, lat_max, lon_min, lon_max):
    """
    Read and crop the dataset to the specified latitude and longitude bounds.
    input:
        downloaded_files (list): List of downloaded file paths.
        lat_min (float): Minimum latitude for cropping.
        lat_max (float): Maximum latitude for cropping.
        lon_min (float): Minimum longitude for cropping.
        lon_max (float): Maximum longitude for cropping.
    output:
        ds (xarray.Dataset): Cropped dataset.
    """
    # Open the downloaded files as an xarray dataset
    ds = xr.open_mfdataset(downloaded_files, group="Grid")

    # Crop the dataset to the specified latitude and longitude bounds
    ds = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    return ds

def plot_test_imerg(ds, lat_min, lat_max, lon_min, lon_max):
    """
    plot the data to check if the data is correct

    Args:
        ds (_type_): _description_
    """
    # Get the precipitation, latitude, and longitude variables
    precip = ds['precipitation'][0,:,:].values
    precip = np.transpose(precip)
    theLats = ds['lat'].values
    theLons = ds['lon'].values
    x, y = np.float32(np.meshgrid(theLons, theLats))
    
    # Set the figure size, projection, and extent
    fig = plt.figure(figsize=(21, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])
    #ax.set_extent([-180, 180, -60, 60])  
    # Add coastlines and formatted gridlines
    ax.coastlines(resolution="110m", linewidth=1)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
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
    norm = BoundaryNorm(clevs, ncolors=plt.cm.rainbow.N, clip=True)

    # Plot the data with pcolormesh
    mesh = plt.pcolormesh(x, y, precip, cmap=plt.cm.rainbow, norm=norm, shading="auto")

    # Add a colorbar
    cb = plt.colorbar(mesh, ax=ax, orientation="vertical", pad=0.05, aspect=16, shrink=0.8)
    cb.set_label('mm / hr', size=20)
    cb.ax.tick_params(labelsize=16)

    # Add a title
    plt.title('GPM IMERG Monthly Mean Rain Rate for January 2014', size=24)

    # Show the plot
    plt.show()


if __name__ == "__main__":
    main()
        