#!/bin/sh
set -x
date

# eparse function
eparse() { set -eux; eval "set -eux; cat<<_EOF"$'\n'"$(< "$1")"$'\n'"_EOF"; }

sorcdir=$(pwd)
workdir=/lfs/h2/emc/ptmp/${USER}/graphics_tmp

mkdir -p ${workdir}
cd ${workdir}

# Copy over the script and config template
cp ${sorcdir}/plotATCF.py ./
cp ${sorcdir}/plotATCF.yml.tmp ./

# Parse the yaml config file
stormModel=${stormModel:-HWRF}
stormName=${stormName:-IDA}
stormID=${stormID:-09L}
stormBasin=${stormBasin:-AL}
ymdh=${ymdh:-2021082800}
adeckFile=${adeckFile:-/lfs/h2/emc/hur/noscrub/emc.hur/trak_save/abdeck/aid_nws/aal092021.dat}
bdeckFile=${bdeckFile:-/lfs/h2/emc/hur/noscrub/emc.hur/trak_save/abdeck/btk/bal092021.dat}
techModels=${techModels:-"['BEST','OFCL','HWRF','HMON','AVNO']"}
techLabels=${techModels}
techColors=${techColors:-"['black','red','purple','green','blue']"}
techMarkers=${techMarkers:-"['hr','.','.','.','.','.']"}
techMarkerSizes=${techMarkerSizes:-"[18,15,15,15,15,15]"}
timeInfo=True; catInfo=True; catRef=True
cartopyDataDir=${cartopyDataDir:-/lfs/h2/emc/hur/noscrub/local/share/cartopy}
eparse plotATCF.yml.tmp > plotATCF.yml

./plotATCF.py

# Trim and combine figures
figpre=${stormName}${stormID}.${ymdh}
convert -trim ${figpre}.track.png PNG8:${figpre}.track.png
convert -geometry x790 -bordercolor White -border 5x5 ${figpre}.track.png ${figpre}.track_x800.png
convert -trim ${figpre}.Vmax.png PNG8:${figpre}.Vmax.png
convert -geometry x390 -bordercolor White -border 5x5 ${figpre}.Vmax.png ${figpre}.Vmax_x400.png
convert -trim ${figpre}.Pmin.png PNG8:${figpre}.Pmin.png
convert -geometry x390 -bordercolor White -border 5x5 ${figpre}.Pmin.png ${figpre}.Pmin_x400.png
convert -gravity east -append ${figpre}.Vmax_x400.png ${figpre}.Pmin_x400.png ${figpre}.intensity_x800.png
convert +append ${figpre}.track_x800.png ${figpre}.intensity_x800.png ${figpre}.fcst.png
convert ${figpre}.fcst.png PNG8:${figpre}.fcst.png

date
echo "job done"
exit
