#!/bin/sh
# Usage:   sh plotATCF.sh STORM STORMID yyyymmddhh MC_MODEL atcffile adeckdir bdeckdir sorcdir workdir archdir
#
##################################################################
set -x
if [ $# -lt 10 ]; then
  echo "USAGE: sh $0 STORM STORMID yyyymmddhh MC_MODEL atcffile adeckdir bdeckdir sorcdir workdir archdir"
  echo "   or  sh $0 STORM STORMID yyyymmddhh MC_MODEL atcffile adeckdir bdeckdir sorcdir workdir archdir modelLabels modelColors modelMarkers"
  echo "ERROR: NEED 9 ARGUMENTS - SCRIPT WILL EXIT"
  exit 1
fi

date

if [ $# -ge 10 ]; then
  STORM=$1
  STORMID=$2
  yyyymmddhh=$3
  MC_MODEL=$4
  atcffile=$5
  adeckdir=$6
  bdeckdir=$7
  sorcdir=$8
  workdir=$9
  archdir=${10}
fi

modelLabels=${11:-""}
modelColors=${12:-""}
modelMarkers=${13:-""}

echo 'STORM=' ${STORM}
echo 'STORMID=' ${STORMID}
echo 'yyyymmddhh=' ${yyyymmddhh}
echo 'MC_MODEL=' ${MC_MODEL}
echo 'atcf file=' $atcffile
echo 'adeck dir=' $adeckdir
echo 'bdeck dir=' $bdeckdir
echo 'sorcdir=' $sorcdir
echo 'archdir=' $archdir
echo 'modelLabels=' $modelLabels
echo 'modelColors=' $modelColors
echo 'modelMarkers=' $modelMarkers

storm=`echo ${STORM} | tr '[A-Z]' '[a-z]'`
stormid=`echo ${STORMID} | tr '[A-Z]' '[a-z]' `
num=`echo ${stormid} | cut -c1-2`
cyc=`echo ${yyyymmddhh} | cut -c9-10`
yyyy=`echo ${yyyymmddhh} | cut -c1-4`
mm=`echo ${yyyymmddhh} | cut -c5-6`

echo 'storm=' ${storm}
echo 'cyc=' ${cyc}
echo 'stormid=' ${stormid}
echo 'num=' ${num}
echo 'yyyy=' ${yyyy}
echo 'mm=' ${mm}

basin1c=`echo ${stormid} | cut -c3`
echo 'basin1c=' ${basin1c}
if [ ${basin1c} = 'l' ]; then
 basin2c='al'
elif [ ${basin1c} = 'e' ]; then
 basin2c='ep'
elif [ ${basin1c} = 'c' ]; then
 basin2c='cp'
elif [ ${basin1c} = 'w' ]; then
 basin2c='wp'
elif [ ${basin1c} = 's' ] || [ ${basin1c} = 'p'  ]; then
 basin2c='sh'
 if [ ${mm} -ge 7  ]; then
  yyyy=$((${yyyy}+1))
  echo 'TC season of SH basin starts from October.'
  echo ${yyyy}
 fi
elif [ ${basin1c} = 'a' ] || [ ${basin1c} = 'b'  ]; then
 basin2c='io'
else
 echo "ERROR: WRONG BASIN DESIGNATION basin1c=${basin1c}"
 echo 'ERROR: SCRIPT WILL EXIT'
 exit 1
fi

BASIN=`echo ${basin2c} | tr '[a-z]' '[A-Z]'`
adeckfile="a${basin2c}${num}${yyyy}.dat"
bdeckfile=b${basin2c}${num}${yyyy}.dat

echo 'archdir=' $archdir
mkdir -p $archdir

work="${workdir}/ATCF/${STORM}${STORMID}/$yyyymmddhh"
echo 'work=' ${work}
mkdir -p ${work}
cd ${work}

#atcffile=${storm}${stormid}.${yyyymmddhh}.trak.hwrf.atcfunix
echo 'atcffile=' ${atcffile}
if [ -s ${atcffile} ]; then
   ln -sf ${atcffile} ./
   cp -p  ${adeckdir}/${adeckfile} ./adeckfile_temp
   ln -sf ${bdeckdir}/${bdeckfile} ./
   trkexist=True
else
   echo "WARNING: ${atcffile} NOT PRESENT OR EMPTY"
   trkexist=False
fi

grep -E "${BASIN}, ${num}.*${yyyymmddhh}" ./adeckfile_temp > ./adeck.tmp
adecktemp="./adeck.tmp"

# Link over the scripts
#cp -p ${sorcdir}/ATCF/*.ncl ./
ln -sf ${sorcdir}/ATCF/*.ncl ./

# run ncl to plot figures
if [ -s ${atcffile} ] || [ -s ${adecktemp} ]; then
 ncl 'stormModel="'${MC_MODEL}'"' \
     'stormName="'${STORM}'"' 'stormID="'${STORMID}'"' \
     'startDate='${yyyymmddhh} \
 	 'atcfFile="'${atcffile}'"' \
     'adeckFile="'${adecktemp}'"' \
     'bdeckFile="'${bdeckfile}'"' \
     'catInfo=True' \
     'modelLabels='${modelLabels} \
     'modelColors='${modelColors} \
     'modelMarkers='$modelMarkers \
	 plot_track.ncl

 figpre=${STORM}${STORMID}.${yyyymmddhh}
 convert -trim ${figpre}.track.png ${figpre}.track.png
 convert -geometry x796 -bordercolor White -border 2x2 \
     ${figpre}.track.png ${figpre}.track_x800.png
#montage -tile 1x -geometry 796x796+2+2 \
#    ${figpre}.track.png ${figpre}.track_x800.png

 ncl 'stormModel="'${MC_MODEL}'"' \
     'stormName="'${STORM}'"' 'stormID="'${STORMID}'"' \
     'startDate='${yyyymmddhh} \
 	 'atcfFile="'${atcffile}'"' \
     'adeckFile="'${adecktemp}'"' \
     'bdeckFile="'${bdeckfile}'"' \
     'catInfo=True' \
     'modelLabels='${modelLabels} \
     'modelColors='${modelColors} \
     'modelMarkers='$modelMarkers \
	 plot_intensity.ncl
 convert -trim ${figpre}.intensity.000001.png ${figpre}.Vmax.png
 convert -trim ${figpre}.intensity.000002.png ${figpre}.Pmin.png

 montage -tile 1x -geometry 656x396+2+2 \
     ${figpre}.Vmax.png ${figpre}.Pmin.png \
	 ${figpre}.intensity_x800.png
 convert +append ${figpre}.track_x800.png ${figpre}.intensity_x800.png ${figpre}.fcst.png

# Deliver figures to archive dir
mkdir -p ${archdir}
cp -p ${work}/${figpre}.Pmin.png ${archdir}
cp -p ${work}/${figpre}.Vmax.png ${archdir}
cp -p ${work}/${figpre}.track.png ${archdir}
cp -p ${work}/${figpre}.fcst.png ${archdir}

else
  echo "WARNING: Empty ${atcffile} and ${adecktemp}"
  echo 'WARNING: Will not plot track intensity'
fi

# Cut and deliver atcf track file to archive dir
if [[ -s ${atcffile} ]]; then
# cat ${work}/$atcffile |cut -c1-117 > ${work}/temp_track
# cp ${work}/temp_track ${archdir}/${atcffile}
  cp -p $atcffile ${archdir}/
else
  echo "WARNING: Empty ${atcffile}"
  echo 'WARNING: Will not deliver track file'
fi

date
echo "job done"
exit
