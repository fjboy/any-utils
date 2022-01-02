import abc
import time

READ_BYTES = 'read_bytes'
WRITE_BYTES = 'write_bytes'
SENT_BYTES = 'sent_bytes'
RECEIVE_BYTES = 'receive_bytes'

MEMORY_USED_BYTES = 'memory_used_bytes'
CPU_PERCENT = 'cpu_percent'
DISK_IO_READ_BYTES = 'disk_read_bytes'
DISK_IO_WRITE_BYTES = 'disk_write_bytes'
NET_IO_SEND_BYTES = 'net_send_bytes'
NET_IO_RECEIVE_BYTES = 'net_receive_bytes'

DISK_IO_READ_BYTES_RATE = 'disk_read_bytes_rate'
DISK_IO_WRITE_BYTES_RATE = 'disk_write_bytes_rate'
NET_IO_SEND_BYTES_RATE = 'net_send_bytes_rate'
NET_IO_RECEIVE_BYTES_RATE = 'net_receive_bytes_rate'

ONE_KB = 1024
ONE_MB = ONE_KB * 1024


class BaseHostMonitorDriver(metaclass=abc.ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.last_time = None
        self.last_diskio = None
        self.last_netio = None

    def _get_delta_disk_io(self, read_bytes, write_bytes):
        if not self.last_diskio:
            disk_io = {READ_BYTES: 0, WRITE_BYTES: 0}
        else:
            delta_read = read_bytes - self.last_diskio[READ_BYTES]
            delta_write = write_bytes - self.last_diskio[WRITE_BYTES]
            disk_io = {READ_BYTES: delta_read, WRITE_BYTES: delta_write}
        self.last_diskio = {READ_BYTES: read_bytes, WRITE_BYTES: write_bytes}
        return disk_io

    def _get_delta_net_io(self, sent_bytes, receive_bytes):
        if not self.last_netio:
            net_io = {SENT_BYTES: 0, RECEIVE_BYTES: 0}
        else:
            net_io = {
                SENT_BYTES: sent_bytes - self.last_netio[SENT_BYTES],
                RECEIVE_BYTES: receive_bytes - self.last_netio[RECEIVE_BYTES]
            }
        self.last_netio = {
            SENT_BYTES: sent_bytes,RECEIVE_BYTES: receive_bytes}
        return net_io

    def _compute_rate(self, metrics, delta_time=None):
        for key in [DISK_IO_READ_BYTES, DISK_IO_WRITE_BYTES,
                    NET_IO_SEND_BYTES, NET_IO_RECEIVE_BYTES]:
            if delta_time:
                metrics[key + '_rate'] = metrics.pop(key) / delta_time
            else:
                metrics[key + '_rate'] = 0
        return metrics

    def _compute_bytes(self, metrics, unit='B'):
        if unit == 'B':
            return metrics
        for key in metrics.keys():
            if 'bytes' not in key:
                continue
            if unit == 'KB':
                metrics[key.replace('bytes', 'kb')] = metrics.pop(key) / ONE_KB
            elif unit == 'MB':
                metrics[key.replace('bytes', 'mb')] = metrics.pop(key) / ONE_MB
        return metrics

    def get_metrics(self, rate=False, cpu_interval=1, unit=None):
        # time.sleep(cpu_interval)
        cpu_percent = self.get_cpu_percent()
        disk_io = self.get_disk_io()
        net_io = self.get_net_io()

        delta_time = time.time() - self.last_time if self.last_time else None
        self.last_time = time.time()

        metrics = {
            MEMORY_USED_BYTES: self.get_vmem_used(),
            CPU_PERCENT: cpu_percent,
            DISK_IO_READ_BYTES: disk_io[READ_BYTES],
            DISK_IO_WRITE_BYTES: disk_io[WRITE_BYTES],
            NET_IO_SEND_BYTES: net_io[SENT_BYTES],
            NET_IO_RECEIVE_BYTES: net_io[RECEIVE_BYTES],
        }

        if rate:
            metrics = self._compute_rate(metrics, delta_time)
        if unit:
            metrics = self._compute_bytes(metrics, unit=unit.upper())
        return metrics

    @abc.abstractmethod
    def get_disk_io(self):
        # return {READ_BYTES: 0, WRITE_BYTES: 0}
        pass

    @abc.abstractmethod
    def get_net_io(self):
        # return {SENT_BYTES: 0, RECEIVE_BYTES: 0}
        pass

    @abc.abstractmethod
    def get_cpu_percent(self, cpu_into='cpu'):
        return 0

    @abc.abstractmethod
    def get_vmem_total(self):
        return 0

    @abc.abstractmethod
    def get_vmem_used(self):
        return 0

    @abc.abstractmethod
    def get_vcore_num(self):
        return 0
