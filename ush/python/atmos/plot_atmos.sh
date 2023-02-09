#!/bin/sh

set -x
export PS4='+ $SECONDS + '
set -xue

# eparse function
eparse() { set -eux; eval "set -eux; cat<<_EOF"$'\n'"$(< "$1")"$'\n'"_EOF"; }

HOMEgraph=${HOMEgraph:-$(pwd)/../../../}
module use ${HOMEgraph}/modulefiles
module load graphics.run.wcoss2
module list

stormModel=HFSA
stormName=FIONA
stormID=07L
stormBasin=AL
ymdh=2022092000
fhhh=f036
COMhafs=/lfs/h2/emc/hur/noscrub/emc.hur/HFSA_sample/hafs/v1.0/hfsa.20220920/00
cartopyDataDir=/lfs/h2/emc/hur/noscrub/local/share/cartopy

for domain in parent storm; do
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
  ./plot_heatflux_wind10m.py
  ./plot_lhtflux_wind10m.py
  ./plot_shtflux_wind10m.py
  ./plot_goes_ir13.py
  ./plot_goes_wv9.py
  ./plot_ssmisf17_mw37ghz.py
  ./plot_ssmisf17_mw91ghz.py

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
