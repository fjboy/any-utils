import psutil

from monitor.host import base


class HostMonitorPsutilDriver(base.BaseHostMonitorDriver):

    def get_vmem_total(self):
        return psutil.virtual_memory().total

    def get_vmem_used(self):
        return psutil.virtual_memory().used

    def get_disk_io(self):
        current_disk_io = psutil.disk_io_counters()
        disk_io = self._get_delta_disk_io(
            current_disk_io.read_bytes, current_disk_io.write_bytes)
        return disk_io

    def get_net_io(self):
        current_net_io = psutil.net_io_counters()
        net_io = self._get_delta_net_io(
            current_net_io.bytes_sent, current_net_io.bytes_recv
        )
        return net_io

    def get_cpu_percent(self, interval=1):
        return psutil.cpu_percent(interval=interval)

    def get_vcore_num(self):
        return psutil.cpu_count()
