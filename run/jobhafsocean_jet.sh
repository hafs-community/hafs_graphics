#!/bin/sh
#BATCH --job-name=jobhafsocean
#SBATCH --account=hwrfv3
#SBATCH --qos=batch
##SBATCH --qos=debug
#SBATCH --nodes=1
##SBATCH --tasks-per-node=24
#SBATCH --tasks-per-node=16
#SBATCH --cpus-per-task=1
#SBATCH -t 01:00:00
##SBATCH -t 00:30:00
##SBATCH --partition=xjet
#SBATCH --partition=sjet
#SBATCH -o jobhafsocean.log.%j
#SBATCH -e jobhafsocean.log.%j
##SBATCH --mem=8000
##SBATCH --exclusive
#SBATCH -D.

set -x

date

YMDH=${1:-${YMDH:-2019082900}}
STORM=${STORM:-NATL}
STORMID=${STORMID:-00L}

HOMEgraph=/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics
#WORKgraph=/your/graph/work/dir # if not specified, a default location relative to COMhafs will be used
#COMgraph=/your/graph/com/dir   # if not specified, a default location relative to COMhafs will be used
COMhafs=/your/hafs/com/dir

export HOMEgraph=${HOMEgraph:-/mnt/lfs4/HFIP/hwrfv3/${USER}/hafs_graphics}
export USHgraph=${USHgraph:-${HOMEgraph}/ush}
export DRIVERDOMAIN=${USHgraph}/driverDomain.sh
export DRIVEROCEAN=${USHgraph}/driverOcean.sh

export COMhafs=${COMhafs:-/hafs/com/${YMDH}/${STORMID}}
export WORKgraph=${WORKgraph:-${COMhafs}/../../../${YMDH}/${STORMID}/emc_graphics}
export COMgraph=${COMgraph:-${COMhafs}/emc_graphics}

stormModel=${stormModel:-HAFS}
is6Hr=${is6Hr:-False}
trackOn=${trackOn:-True}
figTimeLevels=$(seq 0 42)
#is6Hr=${is6Hr:-True}
#figTimeLevels=$(seq 0 20)

source ${USHgraph}/graph_pre_job.sh.inc
export machine=${WHERE_AM_I:-wcoss_cray} # platforms: wcoss_cray, wcoss_dell_p3, hera, orion, jet

export TOTAL_TASKS=${TOTAL_TASKS:-${SLURM_NTASKS:-480}}
export NCTSK=${NCTSK:-16}
export NCNODE=${NCNODE:-16}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

source ${USHgraph}/graph_runcmd.sh.inc

mkdir -p ${WORKgraph}
cd ${WORKgraph}

#Generate the cmdfile
cmdfile='cmdfile'
rm -f $cmdfile
touch $cmdfile

#==============================================================================
# For the ocean figures
#==============================================================================

figScriptAll=( \
  "SSTnc.py" \
  "SSSnc.py" \
  "MLDnc.py" \
  "OHCnc.py" \
  "Z20nc.py" \
  "Z26nc.py" \
  "storm_SST.py" \
  "storm_SSS.py" \
  "storm_MLD.py" \
  "storm_OHC.py" \
  "storm_Z20.py" \
  "storm_Z26.py" \
  "storm_tempZ40m.py" \
  "storm_tempZ70m.py" \
  "storm_tempZ100m.py" \
  "storm_WvelZ40m.py" \
  "storm_WvelZ70m.py" \
  "storm_WvelZ100m.py" \
  )

nscripts=${#figScriptAll[*]}

for((i=0;i<${nscripts};i++));
do

  echo ${figScriptAll[$i]}
  echo "${APRUNS} ${DRIVEROCEAN} $stormModel $STORM $STORMID $YMDH $trackOn ${figScriptAll[$i]} > ${WORKgraph}/$STORM$STORMID.$YMDH.${figScriptAll[$i]%.*}.log 2>&1 ${BACKGROUND}" >> $cmdfile

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
