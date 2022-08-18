# Generic Decision Engine configuration templates

This directory contains generic template configuration files to run Decision Engine


* Files in decisionengine are Decision Engine channel configurations, those files go in /etc/decisionengine/
    * config.d has chennel configurations
    * decision_engine.jsonnet is the top level Decision Engine configuration
    * glideinwms.libsonnet is the GlideinWMS configuration file
* condor/condor_mapfile is the HTCondor map file, this file goes in /etc/condor/certs/condor_mapfile
