# Dockerfile for Kafka

FROM quay.io/signalfuse/maestro-base:14.04-0.1.8.1
MAINTAINER Ian Blenke <ian@blenke.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN apt-get -y install python-pip
RUN pip install kazoo

# Get latest available release of Kafka (no stable release yet).
RUN mkdir -p /opt
RUN git clone https://github.com/apache/kafka.git /opt/kafka
# Checkout "blessed" commit from trunk (we need KAFKA-1092 and KAFKA-1112)
# (KAFKA-1092 was a55ec0620f6ce805fafe2e1d4035ec3e0ab4e0d0)
RUN cd /opt/kafka && git checkout -b blessed 855340a2e65ffbb79520c49d0b9a231b94acd538
RUN cd /opt/kafka && ./sbt update
RUN cd /opt/kafka && ./sbt package
RUN cd /opt/kafka && ./sbt assembly-package-dependency

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
