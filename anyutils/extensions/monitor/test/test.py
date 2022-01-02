import os
import sys
import json
import unittest

from monitor import manager

from monitor.hadoop import hdfs
from monitor.hadoop import yarn

def test_get_host_monitor_driver():
    driver = manager.HostMonitoryManager.get_host_monitor_driver(
        driver=manager.DRIVER_TYPE_PSUTILDRIVER
    )
    assert driver.__module__ == 'monitor.host.psutildriver'
    assert driver.__name__ == 'HostMonitorPsutilDriver'

    driver = manager.HostMonitoryManager.get_host_monitor_driver(
        driver=manager.DRIVER_TYPE_BASHDRIVER
    )
    assert driver.__module__ == 'monitor.host.bashdriver'
    assert driver.__name__ == 'HostMonitorBashDriver'
    
    driver = manager.HostMonitoryManager.get_host_monitor_driver()
    assert driver.__module__ == 'monitor.host.psutildriver'
    assert driver.__name__ == 'HostMonitorPsutilDriver'

    obj = driver()
    obj.get_metrics()
    print(json.dumps(obj.get_metrics(rate=True, unit='mb'), indent=4))


def test_hdfs_collector():
    nn_collector = hdfs.NNJmxCollector('http', '192.168.129.42')
    dn_collector = hdfs.DNJmxCollector('http', '192.168.129.42')
    print(json.dumps(nn_collector.collect(), indent=4))

    print(json.dumps(dn_collector.collect(), indent=4))


def test_yarn_collector():
    rm_collector = yarn.RMJmxCollector('http', '192.168.129.42')
    nm_collector = yarn.NMJmxCollector('http', '192.168.129.42')
    print(json.dumps(rm_collector.collect(), indent=4))
    print(json.dumps(nm_collector.collect(), indent=4))


def test_get_node_resource_available():
    rm_collector = yarn.RMJmxCollector('http', '172.18.1.10')
    print(rm_collector.get_nm_resource_available(use_cache=False))


packages = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'monitor')    # noqa
sys.path.append(packages)                                           # noqa

from monitor.host import bashdriver


class TestHostMonitor(unittest.TestCase):
    
    def setUp(self):
        print('settup')
        self.bash_monitor = bashdriver.HostMonitorProcFileDriver()

    def test_get_cpu_percent(self):
        print(self.bash_monitor.get_cpu_percent())


if __name__ == '__main__':
    unittest.main()
