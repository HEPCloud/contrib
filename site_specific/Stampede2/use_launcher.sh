#!/bin/bash

module load launcher

NUMBEROFNODES=20

export LAUNCHER_WORKDIR=/home1/05501/uscms/launcher

echo "DEBUG: LAUNCHER_WORKDIR=$LAUNCHER_WORKDIR"

export LAUNCHER_JOB_FILE=`mktemp -p $LAUNCHER_WORKDIR 'jobfile.XXXXXXXX'`

echo "DEBUG: LAUNCHER_JOB_FILE=$LAUNCHER_JOB_FILE"

for i in $(seq $NUMBEROFNODES)
do
    echo "$LAUNCHER_WORKDIR/node_wrapper.sh $@" >> $LAUNCHER_JOB_FILE
done

$LAUNCHER_DIR/paramrun

rm -f $LAUNCHER_JOB_FILE
