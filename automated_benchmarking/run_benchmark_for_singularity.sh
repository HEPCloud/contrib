#!/bin/bash
#
# This script prepares the environment to build
# the container to run the test
#
# The only parameter that needs to be set is the first value
# BASE_DIR.  This directory needs to exist, and should be
# on a filesystem with at least 10GB of free disk space
#

#### SET THIS VALUE ####

export OUTPUT_DIR=/opt/hepspec/output

cat - << EOF

This script will download and run the hepspec-test suite.

IMPORTANT NOTE: This system must have the 'extra'
repo enabled or this will not run.

The script is currently set to output in this directory:

 $OUTPUT_DIR

To change this, edit the script and modify the
value of OUTPUT_DIR at the top of the script.

Press [Enter] to continue, or ctrl-C to exit.
EOF
read blah

########################

if [[ ! -v OUTPUT_DIR ]]; then
    echo "OUTPUT_DIR is not set"
    exit 1
fi

if [[ -z $OUTPUT_DIR ]]; then
    echo "OUTPUT_DIR is set to the empty string"
    exit 1
fi


echo "OUTPUT_DIR is set to: $OUTPUT_DIR"

if [ ! -d $OUTPUT_DIR ]; then
    echo $OUTPUT_DIR does not exist.  Trying to create it...
    mkdir -p $OUTPUT_DIR
"run_benchmark.sh" [readonly] 100L, 2398C                                                                                                                                                      1,1           Top fi

rpm -q podman buildah curl screen > /dev/null
if [[ $? -ne 0 ]]; then

  cat > /etc/yum.repos.d/sl-extras.repo << EOF
[sl-extras]
Name=Scientific Linux Extras - $basearch
baseurl=http://linux1.fnal.gov/linux/scientific/7x/external_products/extras/\$basearch/

enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-sl file:///etc/pki/rpm-gpg/RPM-GPG-KEY-sl7

name=SL Extras
priority=30
EOF

  subscription-manager config --rhsm.manage_repos=0
  yum clean all
  yum -y install podman buildah curl screen

fi

echo

echo Retrieving hepspec image from publicregistry.fnal.gov

echo Pulling image...

# podman pull publicregistry.fnal.gov/ssi_images/hepspec-benchmark
singularity build --sandbox --fix-perms hepspec-benchmark docker://publicregistry.fnal.gov/ssi_images/hepspec-benchmark

echo
echo Starting benchmark

COUNT=`cat /proc/cpuinfo | grep -c processor`
for ((i=1;i<=$COUNT;i++));
do
#  OUTDIR=$OUTPUT_DIR/run_${i}
  OUTDIR=$OUTPUT_DIR/hepspec-overlay-$i
  mkdir $OUTDIR
  echo "Starting container ${i}.."
#  podman run -d --rm --name hepspec_${i} -v $OUTDIR:/opt/hepspec/hepspec2006/install/result/ hepspec-benchmark /opt/hepspec/start.sh
  singularity exec --overlay hepspec-overlay-$i -B $OUTDIR:/opt/hepspec/hepspec2006/install/result/ hepspec-benchmark /opt/hepspec/start.sh

done