# prometheus-cloudwatch-exporter-python

# AWS cloudwatch Exporter

AWS cloudwatch exporter for prometheus.io, written in python.

This exporter is based on article: 
(https://medium.com/@ikod/custom-exporter-with-prometheus-b1c23cb24e7a)

## Usage

    python3 collector.py [interval_minutes] [port]

    optional arguments:
      interval_minutes      default 5 
      port                  default  9106 - Listen to this port

#### Example

    docker build -t exporter .
    docker run -it --rm  -p 9106:9106 -v ~/.aws:/home/app/.aws exporter:latest


## Installation

    git clone git@github.com:timtel-k/prometheus-cloudwatch-exporter-python.git
    cd prometheus-cloudwatch-exporter-python
    pip install -r /home/app/pip-requirements.txt


