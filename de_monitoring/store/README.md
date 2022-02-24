# Kafka "store" explanation and configuration

In Fermilab's monitoring ecosystem, [Landscape](https://landscape.fnal.gov), we use a [Kafka](https://kafka.apache.org/) cluster to manage input streams of data. The convention we currently use within our Kafka cluster for each data path consists of three steps:

1.  Establishment of an input topic to accept raw data.
2.  Modification of the raw data by reading from the input topic, making changes, and writing to a digest topic.
3.  Sending the digest data to its final destination (such as an Elasticsearch or Graphite instance).

The second two steps are accomplished via [Logstash](https://www.elastic.co/downloads/logstash) instances run in [Docker](https://www.docker.com/) containers. Included in this directory is a simple sample configuration that can be used to run a Logstash instance.  Simply create the indicated Kafka topics (or create your own names and edit the configuration accordingly), and pass in the logstash configuration file to the Logstash executable via the `-f` flag.

Included in this directory is also a mapping template to use with logstash to send data to Elasticsearch.  NOTE:  This mapping template needs to be updated to match the current schema.
