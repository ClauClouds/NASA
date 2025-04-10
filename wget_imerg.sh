
#!/bin/bash

# get IMERG global daily precipiatation data for given time span, 
# clipped to given lat-lon range
# 
# download content of the list 
#  subset_GPM_3IMERGDE_06_20200130_103831.txt
# 

# go to
#   https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDE_V06/summary
#   -> subset / Get data 
#   select what you need
#   -> subset_GPM_3IMERGDE_06_20200130_103831.txt
#   and download on basis of that list ...
# 





# base url of data
#b_url=https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.06
b_url=https://data.gesdisc.earthdata.nasa.gov/data/GPM_L3/GPM_3IMERGHH.07/2024/001/

# destination directory (database=db)
#db=/data/sfb1211/A01/meteo/imerg
db=/net/ostro/ITCZ/imerg



# go through list
for url in $(less subset_GPM_3IMERGHH_07_20230101_20230110.txt)

  do 
  echo '----------------------------------------'
  echo full filename $url
  echo '----------------------------------------'
  echo '----------------------------------------'

  fn=3B${url##*/3B}

  # Build the full destination file path
  dest_file="$db/$fn"

  wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --content-disposition -i $url

  #wget --load-cookies ~/.urs_cookies --save-cookies ~/.usr_cookies --auth-no-challenge=on --keep-session-cookies --user=cacquist --content-disposition $url -O $url
  #wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --content-disposition -i "subset_GPM_3IMERGHH_07_20250409_130513_.txt" -O   $fn
  

  # put into correct place
  #mv $fn $db/$YYYY/$fn
  # Put into correct place (already saved directly to the destination folder)
  echo "File saved to: $dest_file"
  
  done