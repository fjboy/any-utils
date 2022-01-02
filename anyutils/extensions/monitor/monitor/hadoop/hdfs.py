from monitor.hadoop import base

DEFAULT_NN_COLLECT_METRICS = {
    'Hadoop:service=NameNode,name=FSNamesystem': [
        'CapacityTotal', 'CapacityUsed', 'CapacityUsedNonDFS',
        'CapacityRemaining',
        'BlocksTotal', 'FilesTotal',
        'NumActiveClients'
    ],
    'java.lang:type=OperatingSystem':[
        'TotalPhysicalMemorySize', 'FreePhysicalMemorySize',
        'TotalSwapSpaceSize', 'FreeSwapSpaceSize',
        'SystemCpuLoad', 'ProcessCpuLoad'
    ]
}

DEFAULT_DN_COLLECT_METRICS = {
    'Hadoop:service=DataNode,name=RpcActivityForPort9867':[
        'SentBytes', 'ReceivedBytes',
        'RpcQueueTimeNumOps', 'RpcQueueTimeAvgTime'
    ]
}

class NNJmxCollector(base.BaseJmxCollector):

    def __init__(self, scheme, host,
                 collect_metrics=DEFAULT_NN_COLLECT_METRICS,
                 port=9870,
                 **kwargs):
        super(NNJmxCollector, self).__init__(
            scheme, host, port, collect_metrics, **kwargs
        )


class DNJmxCollector(base.BaseJmxCollector):

    def __init__(self, scheme, host,
                 collect_metrics=DEFAULT_DN_COLLECT_METRICS,
                 port=9864,
                 **kwargs):
        super(DNJmxCollector, self).__init__(
            scheme, host, port, collect_metrics, **kwargs
        )
