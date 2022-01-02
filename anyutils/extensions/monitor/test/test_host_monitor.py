import os
import sys
import time
import unittest

packages = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    # noqa
sys.path.append(packages)                                           # noqa

from monitor.host import bashdriver


class TestHostBashMonitor(unittest.TestCase):

    def setUp(self):
        self.bash_monitor = bashdriver.HostMonitorProcFileDriver()

    def test_last_cpuinfo(self):
        self.assertIsNotNone(
            self.bash_monitor.last_cpuinfo.get('cpu')
        )
        self.assertTrue(
            hasattr(self.bash_monitor.last_cpuinfo.get('cpu'), 'idle')
        )
        self.assertGreater(self.bash_monitor.last_cpuinfo.get('cpu').idle, 0)

    def _do_calculate(self):
        a = 0
        for i in range(1000):
            time.sleep(0.001)
            a += i

    def test_get_cpu_percent(self):
        last_cpu = self.bash_monitor.last_cpuinfo.get('cpu')
        self._do_calculate()
        cpu_percent = self.bash_monitor.get_cpu_percent()
        self.assertNotEqual(cpu_percent, 0, 'calculate is not enough')

        new_cpu = self.bash_monitor.last_cpuinfo.get('cpu')
        idle_percent = (new_cpu.idle - last_cpu.idle) * 100.0 / (
            new_cpu.total() - last_cpu.total())
        self.assertEqual(cpu_percent, 100 - idle_percent)

    def test_get_vmem_used(self):
        mem_used = self.bash_monitor.get_vmem_used()
        self.assertNotEqual(mem_used, 0)
        self.assertLessEqual(mem_used, self.bash_monitor.get_vmem_total())

    def test_get_net_io(self):
        time.sleep(1)
        net_io = self.bash_monitor.get_net_io()
        self.assertGreater(net_io['sent_bytes'], 0, 'net sent_bytes is 0')
        self.assertGreater(net_io['receive_bytes'], 0, 'net sent_bytes is 0')

    def test_get_disk_io(self):
        time.sleep(1)
        with open('test.txt', 'a') as f:
            for _ in range(1000):
                f.write('Hello,word' * 1000 + '\n')
        del f
        with open('test.txt') as f:
            f.readlines()
        disk_io = self.bash_monitor.get_disk_io()
        self.assertGreater(disk_io['write_bytes'], 0, 'disk write_bytes is 0')
        self.assertGreater(disk_io['read_bytes'], 0, 'disk read_bytes is 0')
        os.remove('test.txt')


if __name__ == '__main__':
    unittest.main()
