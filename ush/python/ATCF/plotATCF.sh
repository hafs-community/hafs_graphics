#!/bin/sh
# Usage:   sh plotATCF.sh STORM STORMID yyyymmddhh MC_MODEL atcfdir adeckdir bdeckdir sorcdir workdir archdir
#
##################################################################
set -x
if [ $# -lt 10 ]; then
  echo "USAGE: sh $0 STORM STORMID yyyymmddhh MC_MODEL atcfdir adeckdir bdeckdir sorcdir workdir archdir"
  echo "   or  sh $0 STORM STORMID yyyymmddhh MC_MODEL atcfdir adeckdir bdeckdir sorcdir workdir archdir modelLabels modelColors modelMarkers modelMarkerSizes"
  echo "   or  sh $0 STORM STORMID yyyymmddhh MC_MODEL atcfdir adeckdir bdeckdir sorcdir workdir archdir modelLabels modelColors modelMarkers modelMarkerSizes nset"
  echo "ERROR: NEED 9 ARGUMENTS - SCRIPT WILL EXIT"
  exit 1
fi

# eparse function
eparse() { set -eux; eval "set -eux; cat<<_EOF"$'\n'"$(< "$1")"$'\n'"_EOF"; }

date

if [ $# -ge 10 ]; then
  STORM=$1
  STORMID=$2
  yyyymmddhh=$3
  MC_MODEL=$4
  atcfdir=$5
  adeckdir=$6
  bdeckdir=$7
  sorcdir=$8
  workdir=$9
  archdir=${10}
fi

modelLabels=${11:-}
modelColors=${12:-}
modelMarkers=${13:-}
modelMarkerSizes=${14:-}
nset=${15:-}

echo 'STORM=' ${STORM}
echo 'STORMID=' ${STORMID}
echo 'yyyymmddhh=' ${yyyymmddhh}
echo 'MC_MODEL=' ${MC_MODEL}
echo 'atcf dir=' $atcfdir
echo 'adeck dir=' $adeckdir
echo 'bdeck dir=' $bdeckdir
echo 'sorcdir=' $sorcdir
echo 'archdir=' $archdir
echo 'modelLabels=' $modelLabels
echo 'modelColors=' $modelColors
echo 'modelMarkers=' $modelMarkers
echo 'modelMarkerSizes=' $modelMarkerSizes
echo 'nset=' $nset

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
bdeckfile="b${basin2c}${num}${yyyy}.dat"

echo 'archdir=' $archdir
mkdir -p $archdir

#work="${sorcdir}/tmp/ATCF/${STORM}${STORMID}/$yyyymmddhh"
work="${workdir}/ATCF${nset}/${STORM}${STORMID}/$yyyymmddhh"
echo 'work=' ${work}
mkdir -p ${work}
cd ${work}

cp -p ${adeckdir}/${adeckfile} ./adeckfile_tmp0
cp -p ${bdeckdir}/${bdeckfile} ./bdeckfile

#atcffile=${storm}${stormid}.${yyyymmddhh}.trak.hwrf.atcfunix
atcffile=${stormid}.${yyyymmddhh}.hafs.trak.atcfunix
echo 'atcffile=' ${atcffile}
if [ -s ${atcfdir}/${atcffile} ]; then
   cp -p ${atcfdir}/${atcffile} ./${atcffile}
   trkexist=True
else
   echo "WARNING: ${atcfdir}/${atcffile} NOT PRESENT OR EMPTY"
   trkexist=False
fi

grep -E "${BASIN}, ${num}.*${yyyymmddhh}" ./adeckfile_tmp0 > ./adeckfile_tmp1
if [ -s ./${atcffile} ]; then
  grep -v "${MC_MODEL}," ./adeckfile_tmp1 > ./adeckfile_tmp2
  cat ./${atcffile} >> ./adeckfile_tmp2
fi

#grep ncep ens tracker records
yy=`echo ${yyyymmddhh} |cut -c3-4`
grep -E "^.., ${num}.*${yyyymmddhh}" /lfs/h1/ops/prod/com/ens_tracker/v1.3/global/tracks.atcfunix.${yy} > ./adeck_ens.tmp0
#Rename basin ids
sed -i -e 's/^AA/IO/g' -e  's/^BB/IO/g' -e  's/^SP/SH/g'  -e  's/^SI/SH/g' ./adeck_ens.tmp0
grep -E "${BASIN}, ${num}.*${yyyymmddhh}" ./adeck_ens.tmp0 > ./adeck_ens.tmp1
grep -E " 03, [ACEN].[0-9|M][0-9|N],| 03,  UKX,| 03,  EMX,| 03,  CMC,| 03,  NGX," adeck_ens.tmp1 > ./adeck_ens.tmp2
#Drop off problematic records
#grep -v "  0 ,    0 ,   0,    0, XX,  34, NEQ," adeck_ens.tmp2 > ./adeck_ens.tmp
grep -v -E " 03, [ACEN].[0-9|M][0-9|N],| 03,  UKX,| 03,  EMX,| 03,  CMC,| 03,  NGX," ./adeck.tmp > ./adeck_noens.tmp

cat ./adeckfile_tmp2 ./adeck_noens.tmp ./adeck_ens.tmp > ./adeckfile
adeckfile='./adeckfile'
bdeckfile='./bdeckfile'

if [ -s ${atcffile} ] || [ -s ${adeckfile} ]; then

# Copy over the script and config template
cp -p ${sorcdir}/ATCF/plotATCF.py ./
cp ${sorcdir}/ATCF/plotATCF.yml.tmp ./

# Generate the yaml config file
stormModel=${MC_MODEL}; stormName=${STORM}; stormID=${STORMID}; stormBasin=${BASIN}; ymdh=${yyyymmddhh}
adeckFile=${adeckfile}
bdeckFile=${bdeckfile}
techModels=${modelLabels:-"['BEST','OFCL','HWRF','HMON','AVNO']"}
techLabels=${techModels}
techColors=${modelColors:-"['black','red','purple','green','blue']"}
techMarkers=${modelMarkers:-"['hr','.','.','.','.','.']"}
techMarkerSizes=${modelMarkerSizes:-"[18,15,15,15,15,15]"}
timeInfo=True; catInfo=True; catRef=True
cartopyDataDir=${cartopyDataDir:-/lfs/h2/emc/hur/noscrub/local/share/cartopy}
eparse plotATCF.yml.tmp > plotATCF.yml

./plotATCF.py

# Trim and combine figures
figpre=${stormName}${stormID}.${ymdh}
convert -trim ${figpre}.track.png ${figpre}.track.png
convert -geometry x790 -bordercolor White -border 5x5 ${figpre}.track.png ${figpre}.track_x800.png
convert -trim ${figpre}.Vmax.png ${figpre}.Vmax.png
convert -geometry x390 -bordercolor White -border 5x5 ${figpre}.Vmax.png ${figpre}.Vmax_x400.png
convert -trim ${figpre}.Pmin.png ${figpre}.Pmin.png
convert -geometry x390 -bordercolor White -border 5x5 ${figpre}.Pmin.png ${figpre}.Pmin_x400.png
convert -gravity east -append ${figpre}.Vmax_x400.png ${figpre}.Pmin_x400.png ${figpre}.intensity_x800.png
convert +append ${figpre}.track_x800.png ${figpre}.intensity_x800.png ${figpre}.fcst.png
#convert ${figpre}.track.png PNG8:${figpre}.track.png
#convert ${figpre}.Vmax.png PNG8:${figpre}.Vmax.png
#convert ${figpre}.Pmin.png PNG8:${figpre}.Pmin.png
#convert ${figpre}.fcst.png PNG8:${figpre}.fcst.png

# Deliver figures to archive dir
mkdir -p ${archdir}
cp -p ${work}/${figpre}.Pmin.png  ${archdir}/${figpre}.Pmin${nset}.png
cp -p ${work}/${figpre}.Vmax.png  ${archdir}/${figpre}.Vmax${nset}.png
cp -p ${work}/${figpre}.track.png ${archdir}/${figpre}.track${nset}.png
cp -p ${work}/${figpre}.fcst.png  ${archdir}/${figpre}.fcst${nset}.png
# HWRF website uses a different figure name
#cp -p ${work}/${figpre}.fcst.png  ${archdir}/${figpre}.fsct${nset}.png

else
  echo "WARNING: Empty ${atcffile} and ${adecktemp}"
  echo 'WARNING: Will not plot track intensity'
fi

# Deliver atcf track file to archive dir
if [[ Q${nset} = "Q" ]] && [[ -s ${atcffile} ]]; then
  cp -p ${work}/$atcffile ${archdir}/${atcffile}
else
  echo "WARNING: Empty ${atcffile}"
  echo 'WARNING: Will not deliver track file'
fi

date
echo "job done"
exit
