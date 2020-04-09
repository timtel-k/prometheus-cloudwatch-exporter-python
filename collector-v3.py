import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

from datetime import datetime, timedelta
import re
import boto3


class CustomCollector(object):

    def __init__(self):
        self.__s3 = boto3.client('s3')
        self.__cloudwatch = boto3.client('cloudwatch')
        self.__metrics = self.__get_metrics()

    def __get_metrics(self):
        all_buckets = self.__s3.list_buckets()
        buckets = []
        for bucket in all_buckets["Buckets"]:
            match = re.match(r"jbtc-[0-9]*-query-result", bucket["Name"])
            if match:
                buckets.append(bucket["Name"])
        metrics = []
        for i in range(len(buckets)):
            metrics.append({
                'Id': 'metric_alias_' + str(i),
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/S3',
                        'MetricName': 'BytesDownloaded',
                        'Dimensions': [
                            {
                                'Name': 'FilterId',
                                'Value': 'EntireBucket'
                            },
                            {
                                'Name': 'BucketName',
                                'Value': buckets[i]
                            }
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Sum',
                    'Unit': 'Bytes'
                },
                'ReturnData': True,
            })
        return(metrics)

    def collect(self):

        g = GaugeMetricFamily("BytesDownloaded", 'Bytes Downloaded from aws s3', labels=['s3bucket'])
        response = self.__cloudwatch.get_metric_data(
            MetricDataQueries = self.__metrics,
            StartTime = datetime.now()-timedelta(minutes=7200),
            # StartTime = datetime.now()-timedelta(minutes=5),
            EndTime = datetime.now()
        )
        for metric_result in response['MetricDataResults']:
            g.add_metric([metric_result['Label']], sum( metric_result['Values']))
        yield g

if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
