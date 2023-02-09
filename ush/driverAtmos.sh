#!/bin/sh

set -xe

if [ $# -lt 8 ]; then
  echo "sample usage: ./driverAtmos.sh stormModel stormName stormID startDate stormDomain figScript standardLayer fhhh"
  echo "./driverDomain.sh HAFS IDA 09L 2019082800 grid01 plot_reflectivity.py 1003 f036"
fi

# eparse function
eparse() { set -eux; eval "set -eux; cat<<_EOF"$'\n'"$(< "$1")"$'\n'"_EOF"; }

date

stormModel=${1:-HAFS}
stormname=${2:-NATL}
stormid=${3:-00L}

STORMID=`echo ${stormid} | tr '[a-z]' '[A-Z]' `
stormid=`echo ${stormid} | tr '[A-Z]' '[a-z]' `
STORMNAME=`echo ${stormname} | tr '[a-z]' '[A-Z]' `
stormname=`echo ${stormname} | tr '[A-Z]' '[a-z]' `
STORMMODEL=`echo ${stormModel} | tr '[a-z]' '[A-Z]' `

startDate=${4:-2019082900}
stormDomain=${5:-grid01}
figScript=${6:-"plot_reflectivity.py"}
standardLayer=${7:-1003}
fhhh=${8:-f036}

fntmp=${figScript%.*}
figName=${fntmp#plot_}

COMhafs=${COMhafs:-/hafs/com/${startDate}/${STORMID}}
HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
WORKgraph=${WORKgraph:-${COMhafs}/../../../${startDate}/${STORMID}/emc_graphics}
COMgraph=${COMgraph:-${COMhafs}/emc_graphics}
cartopyDataDir=${cartopyDataDir:-/work/noaa/hwrf/local/share/cartopy}

basin1c=$(echo "$stormid" | cut -c3)
YYYY=$(echo "$startDate" | cut -c1-4)
echo 'basin1c=' ${basin1c}

if [ ${basin1c} = 'l' ]; then
   basin2c='al'
   archive_dir="${COMgraph}/figures/RT${YYYY}_NATL/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${basin1c} = 'e' ]; then
   basin2c='ep'
   archive_dir="${COMgraph}/figures/RT${YYYY}_EPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${basin1c} = 'c' ]; then
   basin2c='cp'
   archive_dir="${COMgraph}/figures/RT${YYYY}_CPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${basin1c} = 'w' ]; then
   basin2c='wp'
   archive_dir="${COMgraph}/figures/RT${YYYY}_WPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${basin1c} = 'a' ] || [ ${basin1c} = 'b' ]; then
   basin2c='io'
   archive_dir="${COMgraph}/figures/RT${YYYY}_NIO/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${basin1c} = 'p' ] || [ ${basin1c} = 's' ]; then
   basin2c='sh'
   archive_dir="${COMgraph}/figures/RT${YYYY}_SH/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
else
  echo "Unknown basin1c = ${basin1c}, not lower case l, e, or c a b s p"
  echo 'Script will exit'
  exit 1
fi
BASIN2C=`echo ${basin2c} | tr '[a-z]' '[A-Z]'`

work_dir="${WORKgraph}/${STORMNAME}${STORMID}/${startDate}.${stormDomain}.${figName}_${standardLayer}_${fhhh}"

rm -rf ${work_dir}
mkdir -p ${work_dir}
cd ${work_dir}

cp -up ${HOMEgraph}/ush/python/atmos/plot_atmos.yml.tmp ${work_dir}/
cp -up ${HOMEgraph}/ush/python/atmos/${figScript} ${work_dir}

# Generate the yaml config file
stormModel=${stormModel}; stormName=${STORMNAME}; stormID=${STORMID}
stormBasin=${BASIN2C}; stormDomain=${stormDomain}
ymdh=${startDate}; fhhh=${fhhh}
standardLayer=${standardLayer}; cartopyDataDir=${cartopyDataDir}

eparse plot_atmos.yml.tmp > plot_atmos.yml

./${figScript}

# Use convert to reduce colors and thus file size
#for file in $(/bin/ls -1 *.png); do convert ${file} PNG8:${file} done
for file in $(/bin/ls -1 *.png); do
  convert -dither FloydSteinberg -colors 256 ${file} ${file}
done

# Deliver figure to archive_dir
mkdir -p ${archive_dir}
cp -up ${work_dir}/${STORMNAME}${STORMID}.${startDate}.${STORMMODEL}.*${figName}.*.png ${archive_dir}

date

echo 'driverAtmos done'
