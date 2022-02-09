# de_monitoring

This directory contains various configurations and instructions for running the DecisionEngine logs --> Elasticsearch pipeline for monitoring purposes.  This pipeline is separate from the built-in DecisionEngine monitoring that uses Prometheus.

The necessary components (in order of operations) are

1. [Filebeat](https://www.elastic.co/downloads/beats/filebeat)
2. [Apache Kafka](https://kafka.apache.org/downloads)
3. [Logstash](https://www.elastic.co/downloads/logstash)
4. [Elasticsearch](https://www.elastic.co/downloads/elasticsearch)
