#!/bin/sh

set -x
export PS4='+ $SECONDS + '
set -xue

# eparse function
eparse() { set -eux; eval "set -eux; cat<<_EOF"$'\n'"$(< "$1")"$'\n'"_EOF"; }

HOMEgraph=/work/noaa/hwrf/save/maristiz/hafs_graphics/
module use ${HOMEgraph}/modulefiles
module load modulefile.graphics.run.orion
module list

stormModel=HAFS
stormName=IDA
stormID=09L
stormBasin=AL
ymdh=2021082800
fhhh=f036
COMhafs=/work2/noaa/hwrf/scrub/bliu/hafs_20220603_v0p3a_hfab/com/2021082800/09L
cartopyDataDir=/work/noaa/hwrf/local/share/cartopy

for domain in grid01 grid02; do
  stormDomain=${domain}
  standardLayer=none
  eparse plot_atmos.yml.tmp > plot_atmos.yml
  ./plot_mslp_wind10m.py
  ./plot_tsfc_mslp_wind10m.py
  ./plot_t2m_mslp_wind10m.py
  ./plot_precip_mslp_thk.py
  ./plot_reflectivity.py
  ./plot_850mb_200mb_vws.py
  ./plot_rhmidlev_hgt_wind.py

  #for level in 850 700 500 200; do
  for level in 850; do
    standardLayer=${level}
    eparse plot_atmos.yml.tmp > plot_atmos.yml
    ./plot_temp_hgt_wind.py
    ./plot_rh_hgt_wind.py
    ./plot_vort_hgt_wind.py
    ./plot_streamline_wind.py
    ./plot_tempanomaly_hgt_wind.py
  done
done

echo 'job done'
