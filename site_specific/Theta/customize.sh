#!/bin/bash
#
# Edit customize.sh as you wish to customize squid.conf.
# It will not be overwritten by upgrades.
# See customhelps.awk for information on predefined edit functions.
# In order to test changes to this, run this to regenerate squid.conf:
#	/local/scratch/uscms//frontier-cache/utils/bin/fn-local-squid.sh
# and to reload the changes into a running squid use
#	/local/scratch/uscms//frontier-cache/utils/bin/fn-local-squid.sh reload
# Avoid single quotes in the awk source or you have to protect them from bash.
#

awk --file `dirname $0`/customhelps.awk --source '{
setoption("cache_peer", "***REMOVED*** parent 3128 0 no-query")
setoption("acl NET_LOCAL src", "127.0.0.1/32")
setoption("cache_mem", "128 MB")
setoptionparameter("cache_dir", 3, "10000")
print
}'
