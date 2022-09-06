#!/bin/sh

if [ $# -lt 12 ]; then
  echo "sample usage: ./driverOcean.sh stormModel stormName stormID startDate trackOn figScript"
  echo "./driverOcean.sh HAFS NATL 00L 2019082900 True SSTnc.py"
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
figScript=${6:-"SSTnc.py"}

COMhafs=${COMhafs:-/hafs/com/${startDate}/${STORMID}}
HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
USHgraph=${USHgraph:-${HOMEgraph}/ush}
WORKgraph=${WORKgraph:-${COMhafs}/../../../${startDate}/${STORMID}/emc_graphics}
COMgraph=${COMgraph:-${COMhafs}/emc_graphics}

atcfFile=${COMhafs}/${stormid}.${startDate}.hafs.trak.atcfunix.all

work_dir="${WORKgraph}/${STORMNAME}${STORMID}/${startDate}.${figScript%.py}"

rm -rf ${work_dir}
mkdir -p ${work_dir}
cd ${work_dir}

cp -up ${USHgraph}/getStormIDs.sh ${work_dir}/
cp -up ${USHgraph}/getStormNames.sh ${work_dir}/
cp -up ${USHgraph}/python/ocean/xgrb2nc.sh ${work_dir}/
ln -sf ${USHgraph}/python/ocean/fixdata ./

# Extract atcfunix track files for individual storms
array=$( sh getStormNames.sh ${atcfFile} ${startDate} )
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
yyyy=`echo ${startDate} | cut -c1-4`

# Do not extract if the storm is not in the focused basin
if [ ${BASIN1C} != ${STORMID: -1} ]; then
  continue
fi

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

storm_atcfFile=${work_dir}/${stormnm}${stid}.${startDate}.trak.hafs.atcfunix
grep "^${BASIN2C}, ${STORMNUM}," ${atcfFile} > ${storm_atcfFile}

done

if [ ${trackOn} = 'True' ]; then
  trackon=Yes
else
  trackon=No
fi

if [ "${figScript:0:5}" = "storm" ]; then # This is for the inner storm domain(s)

#stormatcfs=$(/bin/ls -1 ${COMhafs}/*.atcfunix)
stormatcfs=$(/bin/ls -1 *.atcfunix)
for stormatcf in ${stormatcfs}
do

stormatcffile=$(basename ${stormatcf})
stormnameid=${stormatcffile%%.*}
stormnameid=${stormnameid,,}
STORMNAMEID=`echo ${stormnameid} | tr '[a-z]' '[A-Z]' `
STORMNAMETMP=${STORMNAMEID:0:-3} 
STORMIDTMP=${STORMNAMEID: -3} 
letter=`echo ${stormnameid: -1} |  tr '[A-Z]' '[a-z]' `
YYYY=$(echo "$startDate" | cut -c1-4)

if [ ${STORMNAMEID: -1} != ${STORMID: -1} ]; then
  continue
fi

date
python3 ${USHgraph}/python/ocean/${figScript} ${stormModel,,} ${STORMNAMETMP,,} ${STORMIDTMP,,} ${startDate} ${trackon} ${COMhafs} ${work_dir}
#python3 ${USHgraph}/python/ocean/${figScript} ${stormModel,,} ${STORMNAME,,} ${STORMID,,} ${startDate} ${trackon} ${COMhafs} ${work_dir}
date

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
cp -up ${work_dir}/${STORMNAMEID}.*.f*.png ${archive_dir}

done

else # This is for the whole synoptic domain

date
python3 ${USHgraph}/python/ocean/${figScript} ${stormModel,,} ${STORMNAME,,} ${STORMID,,} ${startDate} ${trackon} ${COMhafs} ${work_dir}
date

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
cp -up ${work_dir}/${STORMNAME}${STORMID}.*.f*.png ${archive_dir}

fi

date

echo 'driverDomain done'

