#!/bin/sh

if [ $# -lt 10 ]; then
  echo "sample usage: ./driverDomain.sh stormModel stormName stormID startDate is6Hr figScript figName standardLayer startTimeLevel endTimeLevel"
  echo "./driverDomain.sh HAFS NATL 00L 2019082900 False fv3_Reflectivity_plot.ncl reflectivity 850 0 0"
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
is6Hr=${5:-False}
figScript=${6:-"fv3_Reflectivity_plot_forStorm.ncl"}
figName=${7:-"storm.reflectivity"}
standardLayer=${8:-850}
startTimeLevel=${9:-0}
endTimeLevel=${10:-42}

COMhafs=${COMhafs:-/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafstmp/hafs_couplehycom_202006_ave/com/${startDate}/${STORMID}}
HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafs_emc_graphics}
WORKgraph=${WORKgraph:-${COMhafs}/../../../${startDate}/${STORMID}/graphics/emc_graphics}
COMgraph=${COMgraph:-${COMhafs}/graphics/emc_graphics}

stormDir=${COMhafs}
atcfFile=${stormDir}/${stormname}${stormid}.${startDate}.trak.hafs.atcfunix.all

work_dir="${WORKgraph}/${STORMNAME}${STORMID}/${startDate}.${figName}_${startTimeLevel}_${endTimeLevel}"

rm -rf ${work_dir}
mkdir -p ${work_dir}
cd ${work_dir}

cp -up ${HOMEgraph}/ush/getStormIDs.sh ${work_dir}/
cp -up ${HOMEgraph}/ush/getStormNames.sh ${work_dir}/

cp -up ${HOMEgraph}/ush/ncl/readTracks.ncl ${work_dir}
cp -up ${HOMEgraph}/ush/ncl/colorPlans.ncl ${work_dir}
cp -up ${HOMEgraph}/ush/ncl/validTime.ncl ${work_dir}
cp -up ${atcfFile} ${work_dir}

cp -up ${HOMEgraph}/ush/ncl/${figScript} ${work_dir}

date
unbuffer ncl 'stormModel="'${stormModel}'"' 'startDate="'${startDate}'"' is6Hr=${is6Hr} standardLayer=${standardLayer} startTimeLevel=${startTimeLevel} endTimeLevel=${endTimeLevel} 'atcfFile="'${atcfFile}'"' 'stormDir="'${stormDir}'"' ${figScript}
date

figNamePre=$(echo "$figName" | cut -c1-5)

if [ "${figNamePre}" = "storm" ]; then # This is for the inner storm domain(s)

array=$( sh getStormNames.sh ${atcfFile} ${startDate} )
for stormnameid in ${array[@]}
do

STORMNAMEID=`echo ${stormnameid} | tr '[a-z]' '[A-Z]' ` 
letter=`echo ${stormnameid: -1} |  tr '[A-Z]' '[a-z]' `
YYYY=$(echo "$startDate" | cut -c1-4)

if [ ${letter} = 'l' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_NATL/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
elif [ ${letter} = 'e' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_EPAC/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
elif [ ${letter} = 'c' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_CPAC/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
elif [ ${letter} = 'w' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_WPAC/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
elif [ ${letter} = 'a' ] || [ ${letter} = 'b' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_NIO/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
elif [ ${letter} = 'p' ] || [ ${letter} = 's' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_SH/${STORMNAMEID}/${STORMNAMEID}.${startDate}"
else
  echo "BASIN DESIGNATION LETTER letter = ${letter} NOT LOWER CASE l, e, or c a b s p"
  echo 'SCRIPT WILL EXIT'
  exit 1
fi

mkdir -p $archive_dir
cp -up ${work_dir}/${STORMNAMEID}*${figName}.f*.png ${archive_dir}

done

else # This is for the whole synoptic domain

letter=$(echo "$stormid" | cut -c3)
YYYY=$(echo "$startDate" | cut -c1-4)

if [ ${letter} = 'l' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_NATL/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${letter} = 'e' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_EPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${letter} = 'c' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_CPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${letter} = 'w' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_WPAC/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${letter} = 'a' ] || [ ${letter} = 'b' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_NIO/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
elif [ ${letter} = 'p' ] || [ ${letter} = 's' ]; then
   archive_dir="${COMgraph}/figures/RT${YYYY}_SH/${STORMNAME}${STORMID}/${STORMNAME}${STORMID}.${startDate}"
else
  echo "BASIN DESIGNATION LETTER letter = ${letter} NOT LOWER CASE l, e, or c a b s p"
  echo 'SCRIPT WILL EXIT'
  exit 1
fi

mkdir -p ${archive_dir}
cp -up ${work_dir}/${STORMNAME}${STORMID}.${startDate}.${STORMMODEL}.${figName}.f*.png ${archive_dir}

fi

date

echo 'driverDomain done'

