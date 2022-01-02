import time
import socket
import logging

from anycode.http import restclient

LOG = logging.getLogger(__name__)


DEFAULT_RETRY_TIMES = 1
DEFAULT_RETRY_INTERVAL = 1
DEFAULT_JMX_URL = '/jmx'
DEFAULT_COLLECTOR_INTERVAL = 10

class BaseJmxClient(restclient.RestClient):

    def __init__(self, scheme, host, port, jmx_url,
                 retry_times=DEFAULT_RETRY_TIMES,
                 retry_interval=DEFAULT_RETRY_INTERVAL,
                 **kwargs):
        super(BaseJmxClient, self).__init__(scheme, host, port, **kwargs)
        self.jmx_url = jmx_url
        self.retry_times = retry_times
        self.retry_interval = retry_interval

    def get_jmx(self, collect_metrics=None):
        retry = 0
        while retry <= self.retry_times:
            try:
                resp = self.get(self.jmx_url)
                return resp.content
            except socket.error:
                LOG.warn('connect to %s failed, retry %s', self.endpoint, retry)
                retry += 1
                time.sleep(self.retry_interval)

        raise Exception(
            'get jmx failed after {0} times, endpoint={1}'.format(
                self.retry_times, self.endpoint)
        )


class BaseJmxCollector(object):

    def __init__(self, scheme, host, port, collect_metrics,
                 collect_interval=DEFAULT_COLLECTOR_INTERVAL,
                 jmx_url=DEFAULT_JMX_URL,
                 **kwargs):
        """collector_metrics: dict
               {
                    'Hadoop:service=NameNode,name=FSNamesystem': [
                        'CapacityTotal', 'CapacityUsed'
                    ],
                }
        """
        self.collect_metrics = collect_metrics
        self.collect_interval = collect_interval
        self.client_kwargs = kwargs
        self.active_host_index = 0
        self.client = BaseJmxClient(
            scheme, host, port, jmx_url,
            **self.client_kwargs
        )
        self.metrics = None

    def get_jmx(self):
        return self.client.get_jmx()

    def set_interval(self, interval):
        self.interval = interval

    def _get_collected_metrics(self, jmx, collect_metrics):
        self.metrics = {}
        collected_beans = set([])
        for bean in jmx.get('beans'):
            if bean.get('name') not in collect_metrics.keys():
                continue
            if bean.get('name') not in self.metrics:
                self.metrics[bean.get('name')] = {}
            for key in collect_metrics.get(bean.get('name')):
                self.metrics[bean.get('name')][key] = bean.get(key)
            collected_beans.add(bean.get('name'))

            if len(collected_beans) == len(collect_metrics.keys()):
                break

        if set(collect_metrics.keys()) - collected_beans:
            LOG.warn('beans not found: %s',
                     collect_metrics - collected_beans)
        return self.metrics

    def collect(self, collect_metrics=None):
        jmx = self.get_jmx()
        if not collect_metrics:
            collect_metrics = self.collect_metrics
        if not collect_metrics:
            return jmx
        else:
            return self._get_collected_metrics(
                jmx, collect_metrics or self.collect_metrics)
