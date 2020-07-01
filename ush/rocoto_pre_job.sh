#! /bin/sh --login
set -x -u -e
date
. $USHgraph/graph_pre_job.sh.inc
exec "$@"
