#!/bin/bash

# clean possible leftovers from previous jobs
/usr/bin/fusermount -u /local/scratch/uscms/cvmfsexec/dist/cvmfs/config-osg.opensciencegrid.org >& /dev/null
/usr/bin/fusermount -u /local/scratch/uscms/cvmfsexec/dist/cvmfs/cms.cern.ch >& /dev/null
/usr/bin/fusermount -u /local/scratch/uscms/cvmfsexec/dist/cvmfs/unpacked.cern.ch >& /dev/null
/usr/bin/fusermount -u /local/scratch/uscms/cvmfsexec/dist/cvmfs/oasis.opensciencegrid.org >& /dev/null
rm -rfd /local/scratch/uscms >& /dev/null

# local squid
mkdir -p /local/scratch/uscms
cd /local/scratch/uscms
tar xzf /projects/HEPCloud-FNAL/frontier-cache_local_scratch.tgz
/local/scratch/uscms/frontier-cache/utils/bin/fn-local-squid.sh start

# cvmfs
mkdir -p /local/scratch/uscms/cvmfs-cache
cd /local/scratch/uscms
tar xzf /projects/HEPCloud-FNAL/cvmfsexec_local_scratch.tgz

# unpriviliged singularity from cvmfs
/local/scratch/uscms/cvmfsexec/cvmfsexec cms.cern.ch unpacked.cern.ch oasis.opensciencegrid.org -- /cvmfs/oasis.opensciencegrid.org/mis/singularity/bin/singularity exec --pid --ipc --contain --bind /etc/hosts --bind /projects/HighLumin --bind /projects/HEPCloud-FNAL --bind /cvmfs --home $HOME /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cms:rhel7 hostname

# locally installed singularity
#/local/scratch/uscms/cvmfsexec/cvmfsexec cms.cern.ch unpacked.cern.ch -- singularity exec -u --pid --ipc --contain --bind /etc/hosts --bind /projects/HighLumin --bind /projects/HEPCloud-FNAL --bind /cvmfs --home $HOME /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cms:rhel7 hostname

/local/scratch/uscms/frontier-cache/utils/bin/fn-local-squid.sh stop

# clean up
rm -rfd /local/scratch/uscms >& /dev/null
