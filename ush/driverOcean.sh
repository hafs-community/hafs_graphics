#!/bin/sh

if [ $# -lt 12 ]; then
  echo "sample usage: ./driverOcean.sh stormModel stormName stormID startDate trackOn figScript"
  echo "./driverOcean.sh HAFS IDA 09L 2021082000 True plot_sst.py"
fi

set -xe

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
isStormDomain=${5:-False}
trackOn=${5:-True}
figScript=${6:-"plot_sst.py"}

fntmp=${figScript%.*}
figtmp="ocean.${fntmp#plot_}"
figName="${figtmp//_/.}"

COMhafs=${COMhafs:-/hafs/com/${startDate}/${STORMID}}
HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
USHgraph=${USHgraph:-${HOMEgraph}/ush}
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

work_dir="${WORKgraph}/${STORMNAME}${STORMID}/${startDate}.${figName}"

rm -rf ${work_dir}
mkdir -p ${work_dir}
cd ${work_dir}

cp -up ${USHgraph}/getStormIDs.sh ${work_dir}/
cp -up ${USHgraph}/getStormNames.sh ${work_dir}/
#cp -up ${USHgraph}/python/ocean/${figScript} ${work_dir}/
cp -up ${USHgraph}/python/ocean/xgrb2nc.sh ${work_dir}/
ln -sf ${USHgraph}/python/ocean/fixdata ./

if [ ${trackOn} = 'True' ]; then
  trackon=Yes
else
  trackon=No
fi

date
python3 ${USHgraph}/python/ocean/${figScript} ${stormModel,,} ${STORMNAME,,} ${STORMID,,} ${startDate} ${trackon} ${COMhafs} ${work_dir}
date

# Use convert to reduce colors and thus file size
for file in $(/bin/ls -1 *.png); do
  convert -dither FloydSteinberg -colors 256 ${file} ${file}
done

for file in $(/bin/ls -1 *.change.f*.png); do
  forig=${file/.change./.}
  fcomb=${file/.change./.combine.}
  convert +append ${forig} ${file} ${fcomb}
done

# Deliver figure to archive_dir
mkdir -p ${archive_dir}
cp -up ${work_dir}/${STORMNAME}${STORMID}.*.f*.png ${archive_dir}

date

echo 'driverOcean done'
