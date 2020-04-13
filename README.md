# AWS cloudwatch Exporter

AWS cloudwatch exporter for prometheus.io, written in python.

This exporter is based on article: 
(https://medium.com/@ikod/custom-exporter-with-prometheus-b1c23cb24e7a)


## Usage

    python3 collector.py [interval_minutes] [port]

    optional arguments:
      interval_minutes      default 5 
      port                  default  9106 - Listen to this port

## Installation

    git clone git@github.com:timtel-k/prometheus-cloudwatch-exporter-python.git
    cd prometheus-cloudwatch-exporter-python
    pip install -r /home/app/pip-requirements.txt
    
#### Example with Docker

    docker build -t exporter .
    docker run -it --rm  -p 9106:9106 -v ~/.aws:/home/app/.aws exporter:latest

#### Example with Helm chart

1.Install chart to cluster
```bash
export AWS_ACCESS_KEY_ID=AKXXXXXXXXXXXXXXXXXH
export AWS_SECRET_ACCESS_KEY=2XXXXXXXXXXXXXXXXXXXXXXXXXXXc
export AWS_DEFAULT_REGION=us-east-1
helm install --name exporter --namespace ns ./cloudwatch-exporter-chart/   --set aws.aws_access_key_id=$AWS_ACCESS_KEY_ID,aws.aws_secret_access_key=$AWS_SECRET_ACCESS_KEY,aws.aws_default_region=$AWS_DEFAULT_REGION  --dry-run --debug
helm install --name exporter --namespace ns ./cloudwatch-exporter-chart/   --set aws.aws_access_key_id=$AWS_ACCESS_KEY_ID,aws.aws_secret_access_key=$AWS_SECRET_ACCESS_KEY,aws.aws_default_region=$AWS_DEFAULT_REGION
```

2. Get the application URL by running these commands:
```bash
export NODE_PORT=$(kubectl get --namespace ns -o jsonpath="{.spec.ports[0].nodePort}" services cloudwatch-exporter-chart-service )
export NODE_IP=$(kubectl get nodes --namespace ns -o jsonpath="{.items[0].status.addresses[0].address}")
echo http://$NODE_IP:$NODE_PORT
```

3. Delete chart from cluster
```bash
helm del --purge exporter
```        
    

