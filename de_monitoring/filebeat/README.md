
# Filebeat installation and configuration

The filebeat service runs on the same machine as the decision engine runs on, or wherever the user desired to read the logfiles (by default in /var/log/decisionengine/).  Follow the filebeat installations appropriate for your OS [here](https://www.elastic.co/downloads/beats/filebeat).  

Edit the filebeat.yml configuration file to do two things (an example filebeat.yml configuration is given in this directory):

1. Read from the decisionengine logs by editing the section `filebeat.inputs`,  `paths` entry, so that it looks at the log file(s) you intend to parse (in the example file, `/var/log/decisionengine/decision_engine_log_structlog_debug.log`).
2. Send the output to the Kafka broker, to a certain topic (in our example, the topic name is `test.hepcloud.de`).

Start filebeat (either running the executable directly, or using the service version of filebeat).

And that's it.  Assuming your Kafka broker is up and running, and the topic you've configured already exists on the Kafka cluster, filebeat should start reading your log files and sending json entries to the Kafka cluster.

