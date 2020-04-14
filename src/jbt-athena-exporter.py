# import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server

from datetime import datetime, timedelta
import re
import boto3
import sys, time


class JbtAthenaExporter(object):
    __minutes = 5
    port = 9106
    __s3 = None
    __cloudwatch_cli = None
    __metrics = None

    def __init__(self, minutes=None, requested_port=None):
        self.__s3 = boto3.client('s3')
        self.__cloudwatch_cli = boto3.client('cloudwatch')
        self.__metrics = self.__get_metrics()
        self.__minutes = JbtAthenaExporter.__minutes if minutes is None else minutes
        JbtAthenaExporter.port = JbtAthenaExporter.port if requested_port is None else requested_port
        print("Polling cloudwatch for {} minutes. Serving at port: {}".format(self.__minutes, JbtAthenaExporter.port))

    def __get_metrics(self):
        all_buckets = self.__s3.list_buckets()
        metrics = []
        for bucket in all_buckets["Buckets"]:
            match = re.match(r"jbtc-[0-9]*-query-result", bucket["Name"])
            if match:
                i = len(metrics)
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
                                    'Value': bucket["Name"]
                                }
                            ]
                        },
                        'Period': 300,
                        'Stat': 'Sum',
                        'Unit': 'Bytes'
                    },
                    'ReturnData': True,
                })
        return metrics

    def collect(self):

        g = GaugeMetricFamily("s3_athena_bytes_downloaded", 'Bytes Downloaded from aws s3', labels=['bucket'])
        end_time = datetime.utcnow()
        response = self.__cloudwatch_cli.get_metric_data(
            MetricDataQueries=self.__metrics,
            StartTime=end_time - timedelta(minutes=self.__minutes),
            EndTime=end_time
        )
        print("========\n{}\n{}\n=======".format(response, end_time))
        for metric_result in response['MetricDataResults']:
            g.add_metric([metric_result['Label']], sum(metric_result['Values']))
        yield g


if __name__ == '__main__':
    requested_port = None if len(sys.argv) < 3 else int(sys.argv[2])
    interval_minutes = None if len(sys.argv) < 2 else int(sys.argv[1])

    REGISTRY.register(JbtAthenaExporter(interval_minutes, requested_port))
    start_http_server(JbtAthenaExporter.port)
    while True:
        time.sleep(1)
