#!/usr/bin/env python

# Start script for the Kafka service.
#
# This is where service configuration before starting the Kafka broker can be
# performed, if needed, for example to configure the Kafka broker ID or port.

import os
import sys

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

KAFKA_CONFIG_FILE = 'config/server.properties'
KAFKA_CONFIG_TEMPLATE = """# Kafka configuration
broker.id=%(broker_id)d
advertised.host.name=%(host_address)s
port=%(broker_port)d

num.network.threads=2
num.io.threads=2

socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

log.dir=/var/lib/kafka/logs
num.partitions=1

log.flush.interval.messages=10000
log.flush.interval.ms=100
log.retention.hours=168
log.segment.bytes=536870912
log.cleanup.interval.mins=1

zookeeper.connect=%(zookeeper_nodes)s
zookeeper.connection.timeout=1000000

kafka.metrics.polling.interval.secs=5
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter
kafka.csv.metrics.dir=/var/lib/kafka/metrics/
kafka.csv.metrics.reporter.enabled=false
"""

# Environment variables driving the Kafka configuration and their defaults.
KAFKA_CONFIG_BROKER_ID = int(os.environ.get('KAFKA_CONFIG_BROKER_ID', 0))
KAFKA_CONFIG_BROKER_PORT = int(os.environ.get('KAFKA_CONFIG_BROKER_PORT', 9092))
KAFKA_CONFIG_ZOOKEEPER_BASE = os.environ.get('KAFKA_CONFIG_ZOOKEEPER_BASE', '')

# Get the container's host address. Required for ZooKeeper-based discovery.
CONTAINER_HOST_ADDRESS = os.environ.get('CONTAINER_HOST_ADDRESS', '')
if not CONTAINER_HOST_ADDRESS:
    sys.stderr.write('Container\'s host address is required for Kafka discovery!\n')
    sys.exit(1)

# ZooKeeper node list, required. Comma-separated list of the ZooKeeper nodes,
# as host:port definitions. If defined, the KAFKA_CONFIG_ZOOKEEPER_BASE will be
# appended to each of them for zNode chroot.
ZOOKEEPER_NODE_LIST = os.environ.get('ZOOKEEPER_NODE_LIST', '')
if not ZOOKEEPER_NODE_LIST:
    sys.stderr.write('ZooKeeper node list is required for the Kafka configuration!\n')
    sys.exit(1)

ZOOKEEPER_NODES = ['%s%s' % (node, KAFKA_CONFIG_ZOOKEEPER_BASE)
        for node in ZOOKEEPER_NODE_LIST.split(',')]

# Generate the Kafka configuration from the defined environment variables.
with open(KAFKA_CONFIG_FILE, 'w+') as conf:
    conf.write(KAFKA_CONFIG_TEMPLATE % {
        'broker_id': KAFKA_CONFIG_BROKER_ID,
        'host_address': CONTAINER_HOST_ADDRESS,
        'broker_port': KAFKA_CONFIG_BROKER_PORT,
        'zookeeper_nodes': ','.join(ZOOKEEPER_NODES),
    })

print 'Kafka will connect to ZooKeeper at', ', '.join(ZOOKEEPER_NODES)

# Start the Kafka broker.
os.execl('bin/kafka-server-start.sh', 'kafka', KAFKA_CONFIG_FILE)
