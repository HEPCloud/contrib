#!/bin/bash

# Needed if jobs use scratch, to avoid overloading it
#module load ooops
# Sets IO limits on scratch
#set_io_param 0 low
# Sets IO limits on work
#set_io_param 1 low

# clean possible leftovers from previous jobs
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/config-osg.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/oasis.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/cms.cern.ch >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/unpacked.cern.ch >& /dev/null
rm -rfd /tmp/uscms >& /dev/null

# SITECONF
mkdir -p /tmp/uscms
cd /tmp/uscms
tar xzf /home1/05501/uscms/launcher/T3_US_TACC.tgz

# cvmfs
mkdir -p /tmp/uscms/cvmfs-cache
cd /tmp/uscms
tar xzf /home1/05501/uscms/launcher/cvmfsexec.tgz
/tmp/uscms/cvmfsexec/umountrepo -a
/tmp/uscms/cvmfsexec/mountrepo config-osg.opensciencegrid.org
/tmp/uscms/cvmfsexec/mountrepo oasis.opensciencegrid.org
/tmp/uscms/cvmfsexec/mountrepo cms.cern.ch
#/tmp/uscms/cvmfsexec/mountrepo unpacked.cern.ch

module load tacc-singularity

export SINGULARITYENV_X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/mis/certificates/

# disable jemalloc virtual memory reuse
export SINGULARITYENV_MALLOC_CONF="retain:false"

#export SINGULARITYENV_LD_PRELOAD=/opt/apps/ooops/1.4/lib/ooops.so
#export SINGULARITY_BIND="/tmp,/scratch,/opt/apps/ooops"
export SINGULARITYENV_LD_PRELOAD=""
export SINGULARITY_BIND="/tmp,/scratch"

$@

/tmp/uscms/cvmfsexec/umountrepo -a

rm -rf /tmp/uscms
