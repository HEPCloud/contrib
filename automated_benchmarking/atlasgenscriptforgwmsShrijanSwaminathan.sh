#!/bin/sh

glidein_config="$1"

# find error reporting helper script
error_gen=`grep '^ERROR_GEN_PATH ' "$glidein_config" | awk '{print $2}'`

cd "$TMP"
OUTPUT_DIR="$TMP/atlasgenbmk"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "$OUTPUT_DIR" does not exist.  Trying to create it...
    if ! mkdir -p "$OUTPUT_DIR"; then
      "$error_gen" -error "atlasgenbmk.sh" "WN_Resource" "Could not create $OUTPUT_DIR"
      exit 1
    fi
fi

COUNT=`cat /proc/cpuinfo | grep -c processor`
singularity run -i -c -e -B "$OUTPUT_DIR":/results /cvmfs/unpacked.cern.ch/gitlab-registry.cern.ch/hep-benchmarks/hep-workloads/atlas-gen-bmk:v2.1 -W --threads $COUNT --events 10
#for future use, change the events to something else other than 10. 10 is just to test if the script works well under gwms

if [ -f "$OUTPUT_DIR/atlas-gen_summary_new.json" ]; then
   cat "$OUTPUT_DIR"/atlas-gen_summary_new.json
else
  "$error_gen" -error "atlasgenbmk.sh" "WN_Resource" "Could not find $OUTPUT_DIR/atlas-gen_summary_new.json"
   exit 1
fi
"$error_gen" -ok "atlasgenbmk.sh"
exit 0