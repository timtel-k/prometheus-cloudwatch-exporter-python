# import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

from datetime import datetime, timedelta
import re
import boto3
import sys, time


class CustomCollector(object):

    def __init__(self, minutes):
        self.__s3 = boto3.client('s3')
        self.__cloudwatch_cli = boto3.client('cloudwatch')
        self.__metrics = self.__get_metrics()
        self._minutes = minutes

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
        return (metrics)

    def collect(self):

        g = GaugeMetricFamily("s3_athena_bytes_downloaded", 'Bytes Downloaded from aws s3', labels=['bucket'])
        end_time = datetime.utcnow()
        response = self.__cloudwatch_cli.get_metric_data(
            MetricDataQueries=self.__metrics,
            StartTime=end_time - timedelta(minutes=self._minutes),
            EndTime=end_time
        )
        print(response)
        print(end_time)
        print("=================")
        for metric_result in response['MetricDataResults']:
            g.add_metric([metric_result['Label']], sum(metric_result['Values']))
        yield g


if __name__ == '__main__':
    port = 9106 if len(sys.argv) < 3 else int(sys.argv[2])
    interval_minutes = 5 if len(sys.argv) < 2 else int(sys.argv[1])
    print("Polling cloudwatch for {} minutes. Serving at port: {}".format(interval_minutes, port))

    REGISTRY.register(CustomCollector(interval_minutes))
    start_http_server(port)
    while True:
        time.sleep(1)
