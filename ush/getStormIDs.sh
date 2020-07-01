#!/bin/sh

atcfFile=$1  #"/gpfs/dell2/emc/modeling/noscrub/Bin.Liu/hafstrak/HFC0_2019/barbara02e.2019070206.trak.hafs.atcfunix.all" # "natl00l.2018091000.trak.hafs.atcfunix.all"
##yyyymmddhh=2018091000
##tp='tp'

#awk '{print $1 $2}' $atcfFile > ids.txt
#sort ids.txt | uniq -d > ids2.txt
#array=( $(sed 's/,//; s/,//' ids2.txt) )
array=( $( awk '{print $1 $2}' ${atcfFile} | sort -u | sed 's/,//; s/,//' ) )
#rm ids.txt
#rm ids2.txt
#count=0
IDArray=()
for id in ${array[@]}
do
 
  basin=$(echo "$id" | cut -c1-2)
  number=$(echo "$id" | cut -c3-4)
  
 if [ ${basin} = 'AL' ]; then
    letter='l'
 elif [ ${basin} = 'EP' ]; then
    letter='e'
 elif [ ${basin} = 'CP' ]; then
    letter='c'
 elif [ ${basin} = 'WP' ]; then
    letter='w'
 elif [ ${basin} = 'AA' ]; then
    letter='a'
 elif [ ${basin} = 'BB' ]; then
    letter='b'
 elif [ ${basin} = 'SI' ]; then
    letter='s'
 elif [ ${basin} = 'SP' ]; then
    letter='p'
 fi

 
 stormid=$number$letter
 if [ $number != "00" ]; then
    #array[$count]=$stormid
    IDArray=( "${IDArray[@]}" $stormid )
    #count=$((count + 1))
 fi
done
echo ${IDArray[@]}


