import json

from monitor.hadoop import base

QUEUE_METRICS_ROOT = 'Hadoop:service=ResourceManager,name=QueueMetrics,q0=root'
NM_METRICS = 'Hadoop:service=NodeManager,name=NodeManagerMetrics'
OPERATING_SYSTEM = 'java.lang:type=OperatingSystem'
RM_NM_INFO = 'Hadoop:service=ResourceManager,name=RMNMInfo'
DEFAULT_RM_COLLECT_METRICS = {
    RM_NM_INFO: ['LiveNodeManagers'],
    QUEUE_METRICS_ROOT: [
        'AppsSubmitted', 'AppsRunning', 'AppsPending',
        'AppsCompleted', 'AppsKilled', 'AppsFailed',
        'AvailableMB', 'AllocatedMB', 'ReservedMB',
        'AvailableVCores', 'AllocatedVCores', 'ReservedVCores'
    ],
}
DEFAULT_NM_COLLECT_METRICS = {
    NM_METRICS: [
        'AvailableGB', 'AvailableVCores',
        'NodeUsedMemGB', 'NodeUsedVMemGB',
        'NodeCpuUtilization',
    ],
    OPERATING_SYSTEM: [
        'TotalPhysicalMemorySize', 'FreePhysicalMemorySize',
        'SystemCpuLoad', 'ProcessCpuLoad'
    ]
}
RESOURCE_AVAILABLE_COLLECT = {
    NM_METRICS: [
        'AvailableGB', 'AvailableVCores',
        'NodeCpuUtilization',
    ],
    OPERATING_SYSTEM: [
        'FreePhysicalMemorySize',
    ]
}


class NMResourceAvailble(object):

    def __init__(self, vcores, memory, phy_cpu, phy_mem):
        self.vcores = vcores
        self.memory = memory
        self.phy_cpu = phy_cpu
        self.phy_mem = phy_mem

    def __eq__(self, other):
        if self.vcores == other.vcores and \
           self.memory == other.memory and \
           self.phy_cpu == other.phy_cpu and \
           self.phy_mem == other.phy_mem:
            return True
        return False

    def __gt__(self, other):
        if self.vcores != other.vcores:
            return self.vcores > other.vcores
        if self.memory != other.memory:
            return self.memory > other.memory
        if self.phy_cpu != other.phy_cpu:
            return self.phy_cpu > other.phy_cpu
        if self.phy_mem != other.phy_mem:
            return self.phy_mem > other.phy_mem
        return False


class RMJmxCollector(base.BaseJmxCollector):

    def __init__(self, scheme, host,
                 collect_metrics=DEFAULT_RM_COLLECT_METRICS,
                 port=8088,
                 **kwargs):
        super(RMJmxCollector, self).__init__(
            scheme, host, port, collect_metrics, **kwargs
        )
        self.live_nm = {}

    def get_live_nms(self, use_cache=False):
        live_nodemanagers = {}
        if use_cache and self.metrics:
            live_nodemanagers = self.metrics.get(
                RM_NM_INFO, {}).get('LiveNodeManagers', None)
        if not live_nodemanagers:
            live_nodemanagers = self.collect(collect_metrics={
                RM_NM_INFO: ['LiveNodeManagers']
            }).get(RM_NM_INFO).get('LiveNodeManagers')
            self.metrics[RM_NM_INFO] = {
                'LiveNodeManagers': live_nodemanagers
            }
        live_nm = {}
        for nm in json.loads(live_nodemanagers):
            live_nm[nm.get('NodeId')] = nm
        return live_nm

    def get_nm_resource_available(self, use_cache=True, scheme='http',
                                  monitor_hosts=None):
        resource_available = []
        for node_id, nm_info in self.get_live_nms(use_cache=use_cache).items():
            if nm_info.get('State') == 'RUNNING':
                host, port = nm_info.get('NodeHTTPAddress').split(':')
                if monitor_hosts and host not in monitor_hosts:
                    continue
                nm_collector = NMJmxCollector(scheme, host, port)
                resource_available.append({
                    'node_id': node_id,
                    'containers': nm_info.get('NumContainers'),
                    'availble': nm_collector.get_resource_available()
                })
        return resource_available


class NMJmxCollector(base.BaseJmxCollector):

    def __init__(self, scheme, host,
                 collect_metrics=DEFAULT_NM_COLLECT_METRICS,
                 port=8042,
                 **kwargs):
        super(NMJmxCollector, self).__init__(
            scheme, host, port, collect_metrics, **kwargs
        )

    def get_resource_available(self):
        metrics = self.collect(RESOURCE_AVAILABLE_COLLECT)
        available_vmem = metrics.get(NM_METRICS).get('AvailableGB')
        available_vcores = metrics.get(NM_METRICS).get('AvailableVCores')
        available_cpu = metrics.get(NM_METRICS).get('NodeCpuUtilization')
        available_pmem = metrics.get(OPERATING_SYSTEM).get(
            'FreePhysicalMemorySize')
        return NMResourceAvailble(available_vcores, available_vmem,
                                  2 - available_cpu,
                                  available_pmem)
