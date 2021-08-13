#!/bin/sh

#module load wgrib2

set -x

var=$1
infile=$2
outfile=$3

${WGRIB2:-wgrib2} $infile -match $var -netcdf $outfile

