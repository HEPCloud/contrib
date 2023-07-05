# Generic Decision Engine configuration templates for EL9

This directory contains generic template configuration files to run Decision Engine as pressure-based resource provisioner.


* Files in this directory are the Decision Engine channel configurations, they go in `/etc/decisionengine/`
    * config.d has channel configurations
    * decision_engine.jsonnet is the top level Decision Engine configuration (merge it with your version)
    * glideinwms.libsonnet is the GlideinWMS (pressure-based provisioner) configuration file

Most of the files contain `@TEMPLATE...@` placeholders that need to be changed to reflect your specific setup.
E.g. Assuming a Decision Engine colocated with User pool and Scheduler on `host1.domain` and a GlideinWMS Factory on `host2.domain`, 
you can use the following:
```
TEMPLATE_DE_NAME: (Name for the DE) de_host1
TEMPLATE_FACTORY_DN: Check the DN of host2.domain host certificate
TEMPLATE_FACTORY: (Factory host name) host2.domain
TEMPLATE_SCHEDD_DN: Check the DN of host1.domain host certificate
TEMPLATE_SCHEDD: (Schedd host name) host1.domain
TEMPLATE_SciToken_PATH: Path of the file with the SciToken (where you save it, e.g. using htgettoken)
TEMPLATE_DEHOST: (DE host name) host1.domain
TEMPLATE_POOL_DN: Check the DN of host1.domain host certificate
TEMPLATE_POOL: (User Pool host name) host1.domain
TEMPLATE_SITE: GLIDEIN_Site attr(ibute) of the selected CE in the Factory configuration
```
