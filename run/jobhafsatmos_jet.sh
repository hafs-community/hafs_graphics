#!/bin/sh
#SBATCH --job-name=jobhafsgraph
#SBATCH --account=hwrfv3
#SBATCH --qos=batch
##SBATCH --qos=debug
#SBATCH --nodes=10
#SBATCH --tasks-per-node=12
#SBATCH --cpus-per-task=1
#SBATCH -t 01:00:00
##SBATCH -t 00:30:00
#SBATCH --partition=xjet
##SBATCH --partition=orion
#SBATCH -o jobhafsgraph.log.%j
#SBATCH -e jobhafsgraph.log.%j
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH -D.

set -x

date

YMDH=${1:-${YMDH:-2021082800}}
STORM=${STORM:-IDA}
STORMID=${STORMID:-09L}
stormModel=${stormModel:-HFSA}
fhhhAll=$(seq -f "f%03g" 0 3 126)

#HOMEgraph=/your/graph/home/dir
#WORKgraph=/your/graph/work/dir # if not specified, a default location relative to COMhafs will be used
#COMgraph=/your/graph/com/dir   # if not specified, a default location relative to COMhafs will be used
#COMhafs=/your/hafs/com/dir

export HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
export USHgraph=${USHgraph:-${HOMEgraph}/ush}
export DRIVERSH=${USHgraph}/driverAtmos.sh

export COMhafs=${COMhafs:-/hafs/com/${YMDH}/${STORMID}}
export WORKgraph=${WORKgraph:-${COMhafs}/../../../${YMDH}/${STORMID}/emc_graphics}
export COMgraph=${COMgraph:-${COMhafs}/emc_graphics}

source ${USHgraph}/graph_pre_job.sh.inc
export machine=${WHERE_AM_I:-wcoss2} # platforms: wcoss2, hera, orion, jet
if [ ${machine} = jet ]; then
  export cartopyDataDir=${cartopyDataDir:-/mnt/lfs4/HFIP/hwrfv3/local/share/cartopy}
elif [ ${machine} = hera ]; then
  export cartopyDataDir=${cartopyDataDir:-/scratch1/NCEPDEV/hwrf/noscrub/local/share/cartopy}
elif [ ${machine} = orion ]; then
  export cartopyDataDir=${cartopyDataDir:-/work/noaa/hwrf/noscrub/local/share/cartopy}
elif [ ${machine} = wcoss2 ]; then
  export cartopyDataDir=${cartopyDataDir:-/lfs/h2/emc/hur/noscrub/local/share/cartopy}
else
  export cartopyDataDir=${cartopyDataDir:-/your/local/share/cartopy}
fi

export TOTAL_TASKS=${TOTAL_TASKS:-${SLURM_NTASKS:-480}}
export NCTSK=${NCTSK:-10}
export NCNODE=${NCNODE:-10}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

source ${USHgraph}/graph_runcmd.sh.inc

mkdir -p ${WORKgraph}
cd ${WORKgraph}

#Generate the cmdfile
cmdfile="cmdfile.$STORM$STORMID.$YMDH"
rm -f $cmdfile
touch $cmdfile

for fhhh in ${fhhhAll}; do

for stormDomain in parent storm; do

if [ ${stormDomain} = "parent" ]; then
  figScriptAll=( \
    plot_mslp_wind10m.py \
    plot_tsfc_mslp_wind10m.py \
    plot_t2m_mslp_wind10m.py \
    plot_heatflux_wind10m.py \
    plot_shtflux_wind10m.py \
    plot_lhtflux_wind10m.py \
    plot_precip_mslp_thk.py \
    plot_reflectivity.py \
    plot_goes_ir13.py \
    plot_goes_wv9.py \
    plot_ssmisf17_mw37ghz.py \
    plot_ssmisf17_mw91ghz.py \
    plot_850mb_200mb_vws.py \
    plot_rhmidlev_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_streamline_wind.py \
    )
  levAll=( \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    850 \
    700 \
    500 \
    200 \
    850 \
    700 \
    500 \
    200 \
    850 \
    700 \
    500 \
    200 \
    850 \
    )
elif [ ${stormDomain} = "storm" ]; then
  figScriptAll=( \
    plot_mslp_wind10m.py \
    plot_tsfc_mslp_wind10m.py \
    plot_t2m_mslp_wind10m.py \
    plot_heatflux_wind10m.py \
    plot_shtflux_wind10m.py \
    plot_lhtflux_wind10m.py \
    plot_precip_mslp_thk.py \
    plot_reflectivity.py \
    plot_goes_ir13.py \
    plot_goes_wv9.py \
    plot_ssmisf17_mw37ghz.py \
    plot_ssmisf17_mw91ghz.py \
    plot_rhmidlev_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_temp_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_rh_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_vort_hgt_wind.py \
    plot_streamline_wind.py \
    plot_tempanomaly_hgt_wind.py \
    )
  levAll=( \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    1003 \
    850 \
    700 \
    500 \
    200 \
    850 \
    700 \
    500 \
    200 \
    850 \
    700 \
    500 \
    200 \
    850 \
    200 \
    )
fi
nscripts=${#figScriptAll[*]}

for((i=0;i<${nscripts};i++)); do
  echo ${figScriptAll[$i]} ${levAll[$i]}
# echo "${APRUNS} ${DRIVERSH} $stormModel $STORM $STORMID $YMDH $stormDomain ${figScriptAll[$i]} ${levAll[$i]} $fhhh > ${WORKgraph}/$STORM$STORMID.$YMDH.${stormDomain}.${figScriptAll[$i]%.*}.${fhhh}.log 2>&1 ${BACKGROUND}" >> $cmdfile
  echo "time ${DRIVERSH} $stormModel $STORM $STORMID $YMDH $stormDomain ${figScriptAll[$i]} ${levAll[$i]} $fhhh > ${WORKgraph}/$STORM$STORMID.$YMDH.${stormDomain}.${figScriptAll[$i]%.*}.${fhhh}.log 2>&1" >> $cmdfile
done

done

done
#==============================================================================

chmod u+x ./$cmdfile
${APRUNC} ${MPISERIAL} -m ./$cmdfile

date

echo 'job done'
