'''
Code to list files under an https: address and save them in txt
format.



'''


# set the directory server from which to list and download files
import pdb


def main():
    
    # define ITCZ domain
    lat_min = -15. # degrees North
    lat_max = 15. # degrees North
    lon_min = -66. # degrees East
    lon_max = 15. # degrees East
    
    # destination folder
    destination_folder = '/data/trade_pc/ITCZ/2024/geost'
    
    # file list filename
    file_list_name = 'file_list.txt'
    
    
    # define url for geostationary data
    # geostationary files available at https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access/
    year = '2024'
    url = 'https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access/'+year+'/'

    # read the list of files from the url
    get_file_list(url, file_list_name='file_list.txt')
    
    # filter lines not ending with .nc
    filter_nc_files('file_list.txt')
    
    # download files from the list 
    download_from_list(url, 
                       file_list_name, 
                       destination_folder,
                       lat_min, 
                       lat_max,
                       lon_min,
                       lon_max)
    
def get_file_list(url, file_list_name='file_list.txt'):
    """
    date = '2025-04-09'
    author = 'cacquist'
    goal = script to print the list of files in a url directory without authentication
    and save them in a text file.
    Args:
        url (str): The URL of the directory to list files from.
        file_list_name (str): The name of the text file to save the file list.
    """ 
    
    import requests
    from bs4 import BeautifulSoup
    
    
    # Fetch the HTML content of the directory
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # open a text file to save the filenames
        with open('file_list.txt', 'w') as file:
            # Find all <a> tags (links) and extract file names
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not href.endswith('/'):  # Exclude subdirectories
                    file.write(href + '\n')  # Write the file name to the text file
        print('the file list has been saved to file_list.txt')
    else:
        print(f"Failed to fetch the directory. HTTP Status Code: {response.status_code}")
        
    return()

def filter_nc_files(file_list_name):
    """
    Filters lines in a text file to keep only those ending with '.nc'.
    
    Args:
        file_list_name (str): The name of the text file to filter.
    """
    # Read all lines from the file
    with open(file_list_name, 'r') as file:
        lines = file.readlines()
    
    # Filter lines that end with '.nc'
    filtered_lines = [line for line in lines if line.strip().endswith('.nc')]
    
    # Overwrite the file with the filtered lines
    with open(file_list_name, 'w') as file:
        file.writelines(filtered_lines)
    print(f"Filtered lines saved to {file_list_name}")
    
    return()

def download_from_list(path_url, file_list_name, destination_folder, lat_min, lat_max, lon_min, lon_max):
    """
    Function to:
    - download files from a list of URLs saved in a text file
    - crop the itcz domain
    - post-process variables to convert in proper units
    - save the files in a specific folder
    
    dependencies:
    - read_crop_geost
    Args:
        path_url (str): The base URL for downloading files.
        file_list_name (str): The name of the text file containing the list of file names.
        destination_folder (str): The folder where downloaded files will be moved.
        lat_min (float): Minimum latitude for filtering files.
        lat_max (float): Maximum latitude for filtering files.
        lon_min (float): Minimum longitude for filtering files.
        lon_max (float): Maximum longitude for filtering files.    
    
    """
    import os
    import requests
    from pathlib import Path 

    # Create the destination folder if it doesn't exist
    destination_folder = '/data/trade_pc/ITCZ/2024/geost'  # Replace with your desired folder path
    Path(destination_folder).mkdir(parents=True, exist_ok=True)
        
    # Read the list of files from the text file
    with open(file_list_name, 'r') as file:
        files = file.readlines()
    
    # Loop through each file and download it
    for file_name in files:
        file_name = file_name.strip()  # Remove any leading/trailing whitespace
        url = path_url + file_name  # Construct the full URL
        
        # check if file already exists
        if os.path.exists(os.path.join(destination_folder, file_name)):
            print(f"File already exists: {file_name}")
            continue
        
        # Download the file
        response = requests.get(url)
        
        if response.status_code == 200:
            
            # Save the file in the current directory
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {file_name}")
            
            # read and crop the file
            ds_out = read_crop_geost(file_name, lat_min, lat_max, lon_min, lon_max)
            
            # drop unnecessary variables
            variables_to_drop = ['calslp_irwin', 'calslp_irwin', 'calslp_irwvp', 'caloff_irwvp', 'vis_rad_slope', 'vis_dc_slope', 'vis_dc_offset', 'irwin_2', 'irwin_3', 'irwvp', 'vschn', 'vschn_2', 'satid_ir', 'satid_wv', 'satid_vs', 'sparse2ir', 'sparse2wv','sparse2vs', 'satid_ir3', 'irwin_vza_adj']
            ds_out = ds_out.drop_vars(variables_to_drop)
            
            # Save the cropped dataset to a new file
            ds_out.to_netcdf(os.path.join(destination_folder, file_name), 
                encoding={'irwin_cdr': {"zlib": True, "complevel": 9}})            
            print(f"Cropped and saved: {file_name} to {destination_folder}")
            
            # Optionally, you can delete the original file after moving
            os.remove(file_name)
           
    return()

def read_crop_geost(file_name, lat_min, lat_max, lon_min, lon_max):
    
    """read file with xaryar and crop the domain
    Args:
        file_name (str): The name of the file to read.
        lat_min (float): Minimum latitude for cropping.
        lat_max (float): Maximum latitude for cropping.
        lon_min (float): Minimum longitude for cropping.
        lon_max (float): Maximum longitude for cropping."""
        
    import xarray as xr
    ds = xr.open_dataset(file_name)
    
    # Crop the dataset to the specified latitude and longitude bounds
    crop_ds = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    # Optionally, you can close the dataset after cropping
    ds.close()
    return crop_ds


if __name__ == "__main__":
    main()
        