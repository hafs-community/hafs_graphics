#!/bin/sh

atcfFile=$1  #"/gpfs/dell2/emc/modeling/noscrub/Bin.Liu/hafstrak/HFC0_2019/barbara02e.2019070206.trak.hafs.atcfunix.all" # "natl00l.2018091000.trak.hafs.atcfunix.all"
yyyymmddhh=$2
##tp='tp'

#awk '{print $1 $2}' $atcfFile > ids.txt
#sort ids.txt | uniq -d > ids2.txt
#array=( $(sed 's/,//; s/,//' ids2.txt) )
array=( $( awk '{print $1 $2}' ${atcfFile} | sort -u | sed 's/,//; s/,//' ) )
#rm ids.txt
#rm ids2.txt
#echo ${array[@]}
#count=0
IDArray=()
for id in ${array[@]}
do
 
  basin=$(echo "$id" | cut -c1-2)
  number=$(echo "$id" | cut -c3-4)
 
  if [ $number != "00" ]; then
 
    if [ ${basin} = 'AL' ]; then
       letter='l'
       basin_letter='al'
    elif [ ${basin} = 'EP' ]; then
       letter='e'
       basin_letter='ep'
    elif [ ${basin} = 'CP' ]; then
       letter='c'
       basin_letter='cp'
    elif [ ${basin} = 'WP' ]; then
       letter='w'
       basin_letter='wp'
    elif [ ${basin} = 'AA' ]; then
       letter='a'
       basin_letter='io'
    elif [ ${basin} = 'BB' ]; then
       letter='b'
       basin_letter='io'
    elif [ ${basin} = 'SI' ]; then
       letter='s'
       basin_letter='sh'
    elif [ ${basin} = 'SP' ]; then
       letter='p'
       basin_letter='sh'
    fi


    yyyy=$(echo "$yyyymmddhh" | cut -c1-4)

    if [ -d /mnt/lfs4/HFIP/hwrf-data/hwrf-input/abdeck/btk ]; then
        bdeck_dir="/mnt/lfs4/HFIP/hwrf-data/hwrf-input/abdeck/btk"
    elif [ -d /scratch1/NCEPDEV/hwrf/noscrub/input/abdeck/btk ]; then
        bdeck_dir="/scratch1/NCEPDEV/hwrf/noscrub/input/abdeck/btk"
    elif [ -d /work/noaa/hwrf/noscrub/input/abdeck/btk ]; then
        bdeck_dir="/work/noaa/hwrf/noscrub/input/abdeck/btk"
    fi
    bdeckfile=$bdeck_dir/b${basin_letter}${number}${yyyy}.dat   #$bdeck_dir/b${basin_letter}${number}${yyyy}.dat
    STORM=$( awk -F', ' '$3 ~ /'${yyyymmddhh}'/ {print $0;}' < $bdeckfile | cut -d',' -f28-28 | xargs  | awk '{print $1}' )

    if [ "Q$STORM" = "Q" ] && [[ $number -ge 90 ]]; then
      STORM=INVEST
    fi
    if [ "Q$STORM" = "Q" ]; then
      STORM=UNNAMED
    fi
    stormid=$number$letter
    STORMID=`echo ${stormid} | tr '[a-z]' '[A-Z]' `


    STORMNAME=$STORM$STORMID
    #array[$count]=$STORMNAME
    #count=$((count + 1))
    IDArray=( "${IDArray[@]}" $STORMNAME )
  fi
done
echo ${IDArray[@]}


