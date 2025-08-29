import google.cloud.logging
import logging
from google.cloud import monitoring_v3
import time

client = google.cloud.logging.Client()
client.setup_logging()

class MetricsHelper:
    def __init__(self, project_id, service_prefix, function_name, environment, geo_region_name, gl_class):
        self.project_id = project_id
        self.service_prefix = service_prefix 
        self.function_name = function_name
        self.environment = environment
        self.geo_region_name = geo_region_name
        self.gl_class = gl_class

    def create_metric_descriptor(self, metric_type, description):
        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{self.project_id}"

        descriptor = {
            "type": f"custom.googleapis.com/{self.service_prefix}/{metric_type}",
            "metric_kind": "GAUGE",
            "value_type": "INT64",
            "description": description,
            "labels": [
                {
                    "key": "function",
                    "value_type": "STRING",
                    "description": "Source function name"
                },
                {
                    "key": "environment",
                    "value_type": "STRING",
                    "description": "Environment (stag/prod)"
                },
                {
                    "key": "geo_region_name",
                    "value_type": "STRING",
                    "description": "Geo Region Name"
                },
                {
                    "key": "gl_class",
                    "value_type": "STRING",
                    "description": "GL Class"
                },
                 {
                    "key": "journal_entry",
                    "value_type": "STRING",
                    "description": "Journal Entry Name"
                }
            ]
        }

        try:
            request = {"name": project_name, "metric_descriptor": descriptor}
            created_descriptor = client.create_metric_descriptor(request=request)
            logging.info(f'Successfully created metric descriptor: {created_descriptor.name}')
            return created_descriptor
        except Exception as e:
            logging.error(f'Failed to create metric descriptor {metric_type}: {str(e)}')
            raise

    def write_metric(self, metric_type, journal_entry_name=None, value=1):
        try:
            logging.info(f"Attempting to write metric {metric_type} with value {value} to project {self.project_id}")
            client = monitoring_v3.MetricServiceClient()

            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/{self.service_prefix}/{metric_type}"
            series.metric.labels.update({
                'function': self.function_name,
                'environment': self.environment,
                'geo_region_name': self.geo_region_name if self.geo_region_name else 'None',
                'gl_class': self.gl_class if self.gl_class else 'None',
                'journal_entry': journal_entry_name if journal_entry_name else 'None'
            })

            series.resource.type = 'global'
            series.resource.labels.update({'project_id': self.project_id})

            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10**9)

            interval = monitoring_v3.TimeInterval({
                'end_time': {'seconds': seconds, 'nanos': nanos},
                'start_time': {'seconds': seconds, 'nanos': nanos}
            })

            point = monitoring_v3.Point({'interval': interval, 'value': {'int64_value': value}})

            series.points = [point]

            logging.info(f"Constructed time series for {metric_type}: {series}")

            client.create_time_series(request={
                "name": f"projects/{self.project_id}",
                "time_series": [series]
            })

            logging.info(f"Successfully wrote metric {metric_type} with value {value}")
        except Exception as e:
            logging.error(f"Failed to write metric {metric_type}: {str(e)}", exc_info=True)

    def setup_metrics(self, metrics):
        logging.info(f"Setting up {len(metrics)} metric descriptors for project {self.project_id}")

        for metric_type, description in metrics:
            try:
                self.create_metric_descriptor(metric_type, description)
            except Exception as e:
                if "Already exists" in str(e):
                    logging.info(f"Metric descriptor {metric_type} already exists")
                else:
                    logging.warning(f"Failed to create metric descriptor {metric_type}: {str(e)}")

        logging.info("Completed metric descriptor setup") 