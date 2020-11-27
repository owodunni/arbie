"""Helper for using prometheus_client."""

import logging

from prometheus_client import Gauge, Summary, start_http_server


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):  # noqa: WPS430
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Prometheus(object):
    def __init__(self):
        try:
            start_http_server(8000)  # noqa: WPS432
        except OSError as e:
            logging.getLogger().info(e)

        self.metric_store = {}

    def gauge(self, name, description):
        return self._get_or_create(name, description, Gauge)

    def summary(self, name, description):
        return self._get_or_create(name, description, Summary)

    def _get_or_create(self, name, description, metric):
        valid_name = self._to_valid_name(name)
        if valid_name in self.metric_store:
            return self.metric_store[valid_name]
        self.metric_store[valid_name] = metric(valid_name, description)
        return self._get_or_create(valid_name, description, metric)

    def _to_valid_name(self, name):
        return name.replace(".", "_").lower()


def get_prometheus():
    return Prometheus()
