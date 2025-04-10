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
b_url = https://arthurhouhttps.pps.eosdis.nasa.gov/gpmdata/2024/01/01/imerg/

# destination directory (database=db)
#db=/data/sfb1211/A01/meteo/imerg
db = /net/ostro/ITCZ/imerg



# go through list
for url in $( less subset_GPM_3IMERGDE_06_20200130_103831.txt )
  do 
  echo '----------------------------------------'

# https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDE.06/2014/01/
#   3B-DAY-E.MS.MRG.3IMERG.20140101-S000000-E235959.V06.nc4
#   0123456789 123456789 123456789 123456789 123456789 123456789 
#   .nc4?precipitationCal[0:0][1050:1150][449:749],HQprecipitation[0:0][1050:1150][449:749],precipitationCal_cnt[0:0][1050:1150][449:749],randomError[0:0][1050:1150][449:749],randomError_cnt[0:0][1050:1150][449:749],time_bnds[0:0][0:1],precipitationCal_cnt_cond[0:0][1050:1150][449:749],HQprecipitation_cnt[0:0][1050:1150][449:749],HQprecipitation_cnt_cond[0:0][1050:1150][449:749],time,lon[1050:1150],lat[449:749],nv


  fn=3B${url##*/3B}
  fn=${fn%.nc4*}

echo fn=$fn

  # date in the form YYYYmmdd
  ymd=${fn:23:8}

echo ymd=$ymd

  # split into parts
  YYYY=${ymd:0:4}
  mm=${ymd:4:2}
  dd=${ymd:6:2}

  # evtly. create directory to store data
  mkdir -p $db/$YYYY

  echo try to get $fn

  # get the data 
  # test with 
  #   wget --load-cookies .usr_cookies --save-cookies .usr_cookies --auth-no-challenge=on --keep-session-cookies --user=jschween --ask-password --content-disposition https://docserver.gesdisc.eosdis.nasa.gov/public/project/GPM/IMERG_ATBD_V06.pdf 
  #   wget --load-cookies .usr_cookies --save-cookies .usr_cookies --auth-no-challenge=on --keep-session-cookies --user=jschween --content-disposition https://gpm1.gesdisc.eosdis.nasa.gov/data/doc/README.GPM.pdf
  # pwd ist das �bliche einfache

  wget --load-cookies .urs_cookies --save-cookies .usr_cookies --auth-no-challenge=on --keep-session-cookies --user=jschween --content-disposition $url -O $fn


  # put into correct place
  mv $fn $db/$YYYY/$fn

  
  done
