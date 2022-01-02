import time
import logging

from monitor.host import base
from monitor.host import procreader

LOG = logging.getLogger(__name__)


class HostMonitorProcFileDriver(object):

    def __init__(self):
        super(HostMonitorProcFileDriver, self).__init__()
        self.last_cpuinfo = procreader.ProcStatContext()
        self.last_procstat = procreader.ProcStatContext()
        self.last_netdev = procreader.ProcNetDevContext()
        self.last_diststats = procreader.DiskStatsContext()

    def get_vmem_total(self):
        mem_info = procreader.MemInfoContext()
        return mem_info.mem_total * 1024

    def get_vmem_used(self):
        mem_info = procreader.MemInfoContext()
        return (mem_info.mem_total - mem_info.mem_free) * 1024

    def get_vcore_num(self):
        return self.last_cpuinfo.get_cpu_num()

    def get_cpu_percent(self, cpu_name='cpu'):
        cpuinfo = procreader.ProcStatContext()

        delta_idle = cpuinfo.get(
            'cpu').idle - self.last_cpuinfo.get('cpu').idle
        delta_total = cpuinfo.get_total(
            'cpu') - self.last_cpuinfo.get_total('cpu')
        self.last_cpuinfo = cpuinfo
        return (100 - delta_idle * 100.0 / delta_total) if delta_total != 0 else 0

    def get_disk_io(self):
        diststats = procreader.DiskStatsContext()
        delta_read = diststats.get_read_bytes() - self.last_diststats.get_read_bytes()
        delta_write = diststats.get_write_bytes() - self.last_diststats.get_write_bytes()
        self.last_diststats = diststats
        return {base.READ_BYTES: delta_read, base.WRITE_BYTES: delta_write}

    def get_net_io(self):
        net_io = procreader.ProcNetDevContext()
        total = net_io.get_total()
        delta_sent_bytes = total['tra_bytes']
        delta_receive_bytes = total['rec_bytes']

        delta_sent_bytes -= self.last_netdev.get_total()['tra_bytes']
        delta_receive_bytes -= self.last_netdev.get_total()['rec_bytes']
        self.last_netdev = net_io
        return {base.SENT_BYTES: delta_sent_bytes,
                base.RECEIVE_BYTES: delta_receive_bytes}

    def get_metrics(self, rate=False, cpu_interval=1, unit=None):
        cpu_percent = self.get_cpu_percent()
        disk_io = self.get_disk_io()
        print('disk io', disk_io)
        net_io = self.get_net_io()
        # delta_time = time.time() - self.last_time if self.last_time else None
        self.last_time = time.time()
        metrics = {
            base.CPU_PERCENT: cpu_percent,
            base.MEMORY_USED_BYTES: self.get_vmem_used(),
            base.NET_IO_SEND_BYTES: net_io[base.SENT_BYTES],
            base.NET_IO_RECEIVE_BYTES: net_io[base.RECEIVE_BYTES],
            base.DISK_IO_READ_BYTES: disk_io[base.READ_BYTES],
            base.DISK_IO_WRITE_BYTES: disk_io[base.WRITE_BYTES],
        }

        # if rate:
        #     metrics = self._compute_rate(metrics, delta_time)
        # if unit:
        #     metrics = self._compute_bytes(metrics, unit=unit.upper())
        return metrics


if __name__ == "__main__":
    monitor = HostMonitorProcFileDriver()
    print(monitor.last_netdev.get_total())
    time.sleep(1)
    print(monitor.get_net_io())
