#==============================================================================
# This script sets job node/core, mpi/omp envionment, and run commands.
#==============================================================================

# Set job node/core, mpi/omp environment
export TOTAL_TASKS=${TOTAL_TASKS:-1}
export NCTSK=${NCTSK:-1}
export OMP_NUM_THREADS=${OMP_THREADS:-${OMP_NUM_THREADS:-24}}
export PURE_OMP_THREADS=${PURE_OMP_THREADS:-${OMP_NUM_THREADS:-24}}
export NCNODE=${NCNODE:-$(($NCTSK * $OMP_NUM_THREADS))}
export KMP_AFFINITY=disabled
export KMP_STACKSIZE=${KMP_STACKSIZE:-2048m}
#export OMP_STACKSIZE=${OMP_STACKSIZE:-2048m}

# Set job run commands
# APRUNE: command to run serial jobs which can share nodes
# APRUNS: command to run serial jobs
# APRUNO: command to run pure openmp jobs
# APRUNC: command to run pure mpi or mpi+omp jobs
# APRUNF: command to run multi jobs from a command file
# BACKGROUND: "" or "&" to implement the APRUNF capability on different platforms
if [ "$machine" = wcoss2 ]; then
  export APRUNE=${APRUNE:-"time"}
  export APRUNS=${APRUNS:-"time"}
  export APRUNO=${APRUNO:-"time"}
  export APRUNC=${APRUNC:-"mpiexec -n ${TOTAL_TASKS} --cpu-bind core --depth ${OMP_NUM_THREADS}"}
  export APRUNF=${APRUNF:-"mpiexec -n ${TOTAL_TASKS} cfp"}
  export APRUNCFP="mpiexec"
  export APRUNO=${APRUNO:-"time"}
  export BACKGROUND=${BACKGROUND:-""}
elif [ "$machine" = jet ] || [ "$machine" = hera ] || [ "$machine" = orion ]; then
  export APRUNE=${APRUNE:-"srun --ntasks=1 --cpus-per-task=1"}
  export APRUNS=${APRUNS:-"srun --ntasks=1 --nodes=1 --ntasks-per-node=1 --cpus-per-task=1"}
  #export APRUNS=${APRUNS:-"srun --exclusive --ntasks=1 --nodes=1 --ntasks-per-node=1 --cpus-per-task=1"}
  export APRUNO=${APRUNO:-"srun --exclusive --ntasks=1 --nodes=1 --ntasks-per-node=${NCTSK} --cpus-per-task=${PURE_OMP_THREADS}"}
  #export APRUNO=${APRUNO:-"srun --ntasks=1 --nodes=1 --ntasks-per-node=${NCTSK} --cpus-per-task=${PURE_OMP_THREADS}"}
  export APRUNC=${APRUNC:-"srun --ntasks=${TOTAL_TASKS} --ntasks-per-node=${NCTSK} --cpus-per-task=${OMP_NUM_THREADS}"}
  #export APRUNF=${APRUNF:-"srun --ntasks=${TOTAL_TASKS} --ntasks-per-node=${NCTSK} --cpus-per-task=${OMP_NUM_THREADS} --multi-prog"}
  #export APRUNF=${APRUNF:-"source"}
  export APRUNF=${APRUNF:-"time"}
  export BACKGROUND=${BACKGROUND:-"&"}
else
  echo "WARNING: unknown platform. Guessing the job run commands..."
  export APRUNE=${APRUNE:-"time"}
  export APRUNS=${APRUNS:-"time"}
  export APRUNO=${APRUNO:-"time"}
  export APRUNC=${APRUNC:-"mpirun"}
  export APRUNF=${APRUNF:-${MPISERIAL:-mpiserial}}
  export BACKGROUND=${BACKGROUND:-""}
fi

# Print out environment
env

#==============================================================================
