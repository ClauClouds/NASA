#!/bin/bash

# script from Jan Schween given on slack on 08/04/2025
# get IMERG global daily precipiatation data for given time span, 
# clip to given lat-lon range
# 
# better use
#   download_v2.sh
# 
# this here is not the best method: 
#   you download the complete earth and clip to the rahter small area ...
# better go to
#   https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDE_V06/summary
#   -> subset / Get data 
#   select what you need
#   -> subset_GPM_3IMERGDE_06_20200130_103831.txt
#   and download on basis of that list ...
# 


# time begin to end as date strings YYYYmmdd
# t_beg_str=20180101
# t_end_str=20180110

# t_beg_str=20180111
# t_end_str=20181231

# t_beg_str=20170101
# t_end_str=20171231

t_beg_str=20140101
t_end_str=20161231


# convert to unix epoch (sec since 1.1.1970)
t_beg=$( date -ud $t_beg_str +%s )
t_end=$( date -ud $t_end_str +%s )


# latitude/longitude range
lat_min=-45.
lat_max=-15.

lon_min=-77.
lon_max=-65.



# base url of data
b_url=https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.06

# destination directory (database=db)
db=/data/sfb1211/A01/meteo/imerg



# steplength in seconds for one day
one_day=86400


# go through days
for t in $( seq $t_beg $one_day $t_end )
  do 
  echo '----------------------------------------'
  echo $(date -ud@$t +%Y.%m.%d/%T )

  # date in the form YYYYmmdd
  ymd=$( date -ud@$t +%Y%m%d )

  # split into parts
  YYYY=${ymd:0:4}
  mm=${ymd:4:2}
  dd=${ymd:6:2}

  # evtly. create directory to store data
  mkdir -p $db/$YYYY

  echo try to get $b_url/$YYYY/$mm/$fn

  # consttruct filename from date
  # https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.06/2018/01/ ...
  #  ... 3B-DAY.MS.MRG.3IMERG.20180101-S000000-E235959.V06.nc4
  fn=3B-DAY.MS.MRG.3IMERG.$ymd-S000000-E235959.V06.nc4

  # get the data 
  wget -q $b_url/$YYYY/$mm/$fn


  # ncks = netcdf kitchen sink: restrict coordinates to Atacama region
  #   -a => do not sort variables
  #   -O => overwrite
  #   -d => restrict dimensions ... -d <dim_name>,<min>,<max>,<step>
  #   -o => ?
  #   
  ncks -a -O -d lat,$lat_min,$lat_max -d lon,$lon_min,$lon_max $fn -o $fn

 
  # put into correct place
  mv $fn $db/$YYYY/$fn

  
  done

