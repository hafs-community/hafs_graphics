#!/bin/sh
#BATCH --job-name=jobhafsgrap
#SBATCH --account=hwrfv3
#SBATCH --qos=batch
##SBATCH --qos=debug
#SBATCH --nodes=30
##SBATCH --tasks-per-node=24
#SBATCH --tasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH -t 03:00:00
##SBATCH -t 00:30:00
##SBATCH --partition=xjet
#SBATCH --partition=sjet
#SBATCH -o jobhafsgraph.log.%j
#SBATCH -e jobhafsgraph.log.%j
##SBATCH --mem=8000
##SBATCH --exclusive
#SBATCH -D.

set -x

date

STORM=${STORM:-NATL}
STORMID=${STORMID:-00L}
YMDH=${YMDH:-2019082900}
HOMEgraph=/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafs_emc_graphics
COMhafs=/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafstmp/hafs_couplehycom_202006_new/com/${YMDH}/${STORMID}

export HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafs_emc_graphics}
export COMhafs=${COMhafs:-/mnt/lfs4/HFIP/hwrfv3/Bin.Liu/hafstmp/HAFS/com/${YMDH}/${STORMID}}
export WORKgraph=${WORKgraph:-${COMhafs}/../../../${YMDH}/${STORMID}/emc_graphics}
export COMgraph=${COMgraph:-${COMhafs}/emc_graphics}
export USHgraph=${USHgraph:-${HOMEgraph}/ush}
export DRIVERDOMAIN=${USHgraph}/driverDomain.sh

stormModel=${stormModel:-HAFS}
is6Hr=${is6Hr:-False}
figTimeLevels=$(seq 0 42)
#is6Hr=${is6Hr:-True}
#figTimeLevels=$(seq 0 20)

source ${USHgraph}/hafs_pre_job.sh.inc
export machine=${WHERE_AM_I:-wcoss_cray} # platforms: wcoss_cray, wcoss_dell_p3, hera, orion, jet
#export RUN_ENVIR=${RUN_ENVIR:-prod}
export RUN_ENVIR=${envir:-prod}
if [ "$RUN_ENVIR" = prod ]; then
  module load ncl
  module list
fi

#####################################
# Set up job node/core/run environment variables
#####################################

export TOTAL_TASKS=${TOTAL_TASKS:-${SLURM_NTASKS:-480}}
export NCTSK=${NCTSK:-16}
export NCNODE=${NCNODE:-16}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

source ${USHgraph}/hafs_runcmd.sh.inc

APRUNS=${APRUNS:-"aprun -b -j1 -n1 -N1 -d1 -cc depth"}
APRUNO=${APRUNO:-"aprun -b -j1 -n1 -N1 -d${PURE_OMP_THREADS} -cc depth"}
APRUNO=${APRUNO:-"time"}
APRUNC=${APRUNC:-"aprun -b -j1 -n${TOTAL_TASKS} -N${NCTSK} -d${OMP_NUM_THREADS} -cc depth"}
APRUNF=${APRUNF:-"aprun -b -j1 -n${TOTAL_TASKS} -N${NCTSK} -d${OMP_NUM_THREADS} -cc depth cfp"}
BACKGROUND=${BACKGROUND:-""}

mkdir -p ${WORKgraph}
cd ${WORKgraph}

#Generate the cmdfile
cmdfile='cmdfile'
rm -f $cmdfile
touch $cmdfile

#==============================================================================
# For the Whole Synoptic Domain
#==============================================================================

figScriptAll=( \
  "fv3_Mslp_10m_Wind_plot.ncl" \
  "fv3_Surface_Temp_Mslp_Wind_plot.ncl" \
  "fv3_Reflectivity_plot.ncl" \
  "fv3_Standard_Layer_Temp_Ght_Wind_plot.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot.ncl" \
  "fv3_Standard_Layer_Streamlines_plot.ncl" \
  "fv3_Standard_Layer_RH_Ght_Wind_plot.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot.ncl" \
  "fv3_Precip_mslp_thickness_plot.ncl" \
  "fv3_Wind_Shear_plot.ncl" \
  )

figNameAll=( \
  "mslp.10m_wind" \
  "surface.temp.mslp.wind" \
  "reflectivity" \
  "850mb.temp.ght.wind" \
  "850mb.vort.hgt.wind" \
  "850mb.wind" \
  "700mb.rh.hgt.wind" \
  "500mb.vort.hgt.wind" \
  "200mb.vort.hgt.wind" \
  "precip.mslp.thk" \
  "wind.shear" \
  )

standardLayerAll=( \
  1003 \
  1003 \
  1003 \
  850 \
  850 \
  850 \
  700 \
  500 \
  200 \
  1003 \
  850 \
  )

nscripts=${#figScriptAll[*]}

for((i=0;i<${nscripts};i++));
do

echo  ${figScriptAll[$i]} ${figNameAll[$i]} ${standardLayerAll[$i]}

for figTimeLevel in ${figTimeLevels};
do
  echo "${APRUNS} ${DRIVERDOMAIN} $stormModel $STORM $STORMID $YMDH $is6Hr ${figScriptAll[$i]} ${figNameAll[$i]} ${standardLayerAll[$i]} $figTimeLevel $figTimeLevel > ${WORKgraph}/$STORM$STORMID.$YMDH.${figNameAll[$i]}.$figTimeLevel.log 2>&1 ${BACKGROUND}" >> $cmdfile
done

done

#==============================================================================
# For the Inner Storm Domain(s)
#==============================================================================

figScriptAll=( \
  "fv3_Mslp_10m_Wind_plot_forStorm.ncl" \
  "fv3_Surface_Temp_Mslp_Wind_plot_forStorm.ncl" \
  "fv3_Reflectivity_plot_forStorm.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot_forStorm.ncl" \
  "fv3_Standard_Layer_Streamlines_plot_forStorm.ncl" \
  "fv3_Standard_Layer_RH_Ght_Wind_plot_forStorm.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot_forStorm.ncl" \
  "fv3_Standard_Layer_Vort_Ght_Wind_plot_forStorm.ncl" \
  "fv3_Standard_Layer_TempAno_forStorm.ncl" \
  )

figNameAll=( \
  "storm.mslp.10m_wind" \
  "storm.surface.temp.mslp.wind" \
  "storm.reflectivity" \
  "storm.850mb.vort.hgt.wind" \
  "storm.850mb.wind" \
  "storm.700mb.rh.hgt.wind" \
  "storm.500mb.vort.hgt.wind" \
  "storm.200mb.vort.hgt.wind" \
  "storm.200mb.tempano" \
  )

standardLayerAll=( \
  1003 \
  1003 \
  1003 \
  850 \
  850 \
  700 \
  500 \
  200 \
  200 \
  )

nscripts=${#figScriptAll[*]}

for((i=0;i<${nscripts};i++));
do

echo  ${figScriptAll[$i]} ${figNameAll[$i]} ${standardLayerAll[$i]}

for figTimeLevel in ${figTimeLevels};
do
  echo "${APRUNS} ${DRIVERDOMAIN} $stormModel $STORM $STORMID $YMDH $is6Hr ${figScriptAll[$i]} ${figNameAll[$i]} ${standardLayerAll[$i]} $figTimeLevel $figTimeLevel > ${WORKgraph}/$STORM$STORMID.$YMDH.${figNameAll[$i]}.$figTimeLevel.log 2>&1 ${BACKGROUND}" >> $cmdfile
done

done

#==============================================================================

if [ "$machine" = hera ] || [ "$machine" = orion ] || [ "$machine" = jet ]; then
  echo 'wait' >> $cmdfile
fi
chmod u+x ./$cmdfile
${APRUNF} ./$cmdfile

wait

date

echo 'job done'
