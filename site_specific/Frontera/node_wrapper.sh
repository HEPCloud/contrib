#!/bin/bash

# clean possible leftovers from previous jobs
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/config-osg.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/oasis.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/cms.cern.ch >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/singularity.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /tmp/uscms/cvmfsexec/dist/cvmfs/unpacked.cern.ch >& /dev/null
rm -rfd /tmp/uscms >& /dev/null

# SITECONF
mkdir -p /tmp/uscms
cd /tmp/uscms
tar xzf /home1/05501/uscms/launcher/T3_US_TACC.tgz

# cvmfs
mkdir -p /tmp/uscms/cvmfs-cache
cd /tmp/uscms
tar xzf /home1/05501/uscms/launcher/cvmfsexec_local_siteconf.tgz

# start local squid
mkdir -p /tmp/uscms
cd /tmp/uscms
tar xzf /home1/05501/uscms/launcher/frontier-cache.tgz
/tmp/uscms/frontier-cache/utils/bin/fn-local-squid.sh start

#module load tacc-singularity
export PATH=/cvmfs/oasis.opensciencegrid.org/mis/singularity/bin:$PATH
export SINGULARITYENV_X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/mis/certificates/
export SINGULARITY_BIND="/tmp"

# disable jemalloc virtual memory reuse
export SINGULARITYENV_MALLOC_CONF="retain:false"

env LD_PRELOAD="" /tmp/uscms/cvmfsexec/cvmfsexec oasis.opensciencegrid.org cms.cern.ch singularity.opensciencegrid.org unpacked.cern.ch -- $@

# cleanup
/tmp/uscms/frontier-cache/utils/bin/fn-local-squid.sh stop
sleep 3
rm -rf /tmp/uscms
