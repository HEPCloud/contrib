# ALCF Theta

ALCF Theta is a KNL based HPC cluster at Argonne Labs

As an LCF it is very restrictive compared to a "standard" grid site. Mainly that means no outbound
internet connectivity from the worker nodes. One can work around this by implementing gateway
services at the edge of the cluster, i.e. the HPC worker node connects to the gateway, which itself
has outbound internet connectivity. At Theta this also runs into technical limitations since the
connection from the worker nodes to the gateway is routed through RSIP, which has a very small
limit on number of connections (order 5 to 10 per node maximum).

At Theta we use:
* site squid proxy maineted by ALCF Theta support
* local node squid proxy that connects to the site squid
* cvmfsexec to mount cvmfs in user space (using site squid proxy)
* stageout wrapper, allowing xrdcp from worker nodes to FNAL dCache (through site squid proxy)

This directory contains:
* customize.sh : configuration for local node squid proxy
* default.local : cvmfsexec configuration
* example_wrapper.sh : example node wrapper script setting up local squid and cvmfsexec
* proxychains.conf : stageout wrapper configuration
* proxychains.sh : stageout wrapper

List of needed external software:
* frontier-squid : https://twiki.cern.ch/twiki/bin/view/Frontier/InstallSquid
* cvmfsexec : https://github.com/cvmfs/cvmfsexec
* proxychains-ng : https://github.com/rofl0r/proxychains-ng

**NB This repository is public, do not add any credential, password, or private information.**
