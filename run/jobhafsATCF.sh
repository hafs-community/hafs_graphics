#!/bin/sh
#
#  echo "Usage:     sh $0 HAFS NATL 00L 2019082900"
#  echo "Usage:     sh $0 HAFS Dorian 05L 2019082900"
#
set -xe

ymdh=${1:-2019082900}
stormModel=${2:-HAFS}
stormname=${3:-NATL}
stormid=${4:-00L}

STORMID=`echo ${stormid} | tr '[a-z]' '[A-Z]' `
stormid=`echo ${stormid} | tr '[A-Z]' '[a-z]' `
STORMNAME=`echo ${stormname} | tr '[a-z]' '[A-Z]' `
stormname=`echo ${stormname} | tr '[A-Z]' '[a-z]' `

#COMhafs=/mnt/lfs4/HFIP/hwrfv3/${USER}/hafstmp/hafsv0p1acpl_202007/com/${ymdh}/${STORMID}
COMhafs=${COMhafs:-/hafs/com/${ymdh}/${STORMID}}
atcfFile=${5:-${COMhafs}/${stormname}${stormid}.${ymdh}.trak.hafs.atcfunix.all}

export HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
export USHgraph=${USHgraph:-${HOMEgraph}/ush}
export WORKgraph=${WORKgraph:-${COMhafs}/../../../${ymdh}/${STORMID}/emc_graphics}
export COMgraph=${COMgraph:-${COMhafs}/emc_graphics}

export ADECKgraph=${ADECKgraph:-/mnt/lfs4/HFIP/hwrf-data/hwrf-input/abdeck/aid}
export BDECKgraph=${BDECKgraph:-/mnt/lfs4/HFIP/hwrf-data/hwrf-input/abdeck/btk}

modelLabels='(/"BEST","'$stormModel'","HWRF","HMON","AVNO","OFCL"/)'
modelColors='(/"black","cyan2","purple","green2","blue","red"/)'
modelMarkers='(/17,18,18,18,18,18/)'

source ${USHgraph}/graph_pre_job.sh.inc
export machine=${WHERE_AM_I:-wcoss_cray} # platforms: wcoss_cray, wcoss_dell_p3, hera, orion, jet

work_dir="${WORKgraph}"
archbase="${COMgraph}/figures"

mkdir -p ${work_dir}
cd ${work_dir}

if [ -f ${atcfFile} ]; then
  atcfFile=${atcfFile}
elif [ -f ${atcfFile%.all} ]; then
  atcfFile=${atcfFile%.all}
else
  echo "File ${atcfFile} does not exist"
  echo 'SCRIPT WILL EXIT'
  exit 1
fi

array=$( sh ${USHgraph}/getStormNames.sh ${atcfFile} ${ymdh} )
echo $array

# Loop for all storms
for stormnmid in ${array[@]}
do
  stormnmid=`echo ${stormnmid} | tr '[A-Z]' '[a-z]' `
  STORMNMID=`echo ${stormnmid} | tr '[a-z]' '[A-Z]' `
  STORMNM=${STORMNMID:0:-3}
  stormnm=${STORMNM,,}
  STID=${STORMNMID: -3}
  stid=${STID,,}
  STORMNUM=${STID:0:2}
  BASIN1C=${STID: -1}
  basin1c=${BASIN1C,,}
  yyyy=`echo ${ymdh} | cut -c1-4`

if [ ${basin1c} = 'l' ]; then
  basin2c='al'
  BASIN2C='AL'
  BASIN='NATL'
elif [ ${basin1c} = 'e' ]; then
  basin2c='ep'
  BASIN2C='EP'
  BASIN='EPAC'
elif [ ${basin1c} = 'c' ]; then
  basin2c='cp'
  BASIN2C='CP'
  BASIN='CPAC'
elif [ ${basin1c} = 'w' ]; then
  basin2c='wp'
  BASIN2C='WP'
  BASIN='WPAC'
elif [ ${basin1c} = 's' ] || [ ${basin1c} = 'p'  ]; then
  basin2c='sh'
  BASIN2C='SH'
  BASIN='SH'
elif [ ${basin1c} = 'a' ] || [ ${basin1c} = 'b'  ]; then
  basin2c='io'
  BASIN2C='IO'
  BASIN='NIO'
else
  echo "WRONG BASIN DESIGNATION basin1c=${basin1c}"
  echo 'SCRIPT WILL EXIT'
  exit 1
fi

  archdir="${archbase}/RT${yyyy}_${BASIN}/${STORMNM}${STID}/${STORMNM}${STID}.${ymdh}"
  storm_atcfFile=${work_dir}/${stormnm}${stid}.${ymdh}.trak.hafs.atcfunix
  grep "^${BASIN2C}, ${STORMNUM}," ${atcfFile} > ${storm_atcfFile}

  if [ -s ${storm_atcfFile} ]; then
    echo "${storm_atcfFile} present, will proceed"
    # make the track and intensity plots
    sh ${HOMEgraph}/ush/plotATCF.sh ${STORMNM} ${STID} ${ymdh} ${stormModel} ${storm_atcfFile} ${ADECKgraph} ${BDECKgraph} ${HOMEgraph}/ush/ncl ${WORKgraph} ${archdir} ${modelLabels} ${modelColors} ${modelMarkers}
  else
    echo "${storm_atcfFile} NOT PRESENT. SKIP."
  fi
done

date

echo 'job done'
