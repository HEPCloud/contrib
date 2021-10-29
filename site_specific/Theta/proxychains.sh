#!/bin/bash

export X509_USER_PROXY=$JOBSTARTDIR/myproxy.pem
export X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/mis/certificates/

/projects/HEPCloud-FNAL/proxychains-ng-4.14/proxychains4 -f /projects/HEPCloud-FNAL/proxychains.conf $@
