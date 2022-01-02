"""
File Reader for linux proc dev
/proc/stat
/proc/meminfo
/proc/net/dev
/proc/diskstats

The /proc/diskstats file displays the I/O statistics of block devices.
Each line contains the following fields:
    1 - major number
    2 - minor mumber
    3 - device name
    4 - reads completed successfully
    5 - reads merged
    6 - sectors read
    7 - time spent reading (ms)
    8 - writes completed
    9 - writes merged
    10 - sectors written
    11 - time spent writing (ms)
    12 - I/Os currently in progress
    13 - time spent doing I/Os (ms)
Example:
    2   0 fd0 0 0 0 0 0 0 0 0 0 0 0
    8  0 sda 47451 241465 3269363 21050 67032 315959 62942464 76693 0 240 7878
    8  1 sda1 215 0 52985 168 10 0 4168 70 0 153 238
    8  2 sda2 47205 241465 3213034 20851 66898 315959 62938296 7659 0 234 7867
    11  0 sr0 0 0 0 0 0 0 0 0 0 0 0
    253  0 dm-0 8768 0 959977 11319 71944 0 60446768 782378 0 15658 793769
    253  1 dm-1 279723 0 2241488 54020 310929 0 2487432 939851 0 9872 993869
    253  2 dm-2 96 0 7073 67 4 0 4096 16 0 59 83
"""
import os

class NetIO(object):

    def __init__(self, line):
        self.columns = line.split()

    def _get_int(self, index):
        return int(self.columns[index])

    @property
    def interface(self):
        return self.columns[0]

    @property
    def rec_bytes(self):
        return self._get_int(1)

    @property
    def rec_packets(self):
        return self._get_int(2)

    @property
    def tra_bytes(self):
        return self._get_int(9)

    @property
    def tra_packets(self):
        return self._get_int(10)


class ProcNetDevContext(object):
    PROC_NET_DEV = '/proc/net/dev'

    def __init__(self):
        self.net_io = {}
        lines = []
        with open(self.PROC_NET_DEV) as f:
            lines = f.readlines()
        for line in lines[2:]:
            net_io = NetIO(line)
            self.net_io[net_io.interface] = net_io

    def ifaces(self):
        return self.net_io.keys()

    def get(self, interface):
        return self.net_io.get(interface)

    def get_total(self, iface=None):
        total = {
            'rec_bytes': 0,
            'rec_packets': 0,
            'tra_bytes': 0,
            'tra_packets': 0,
        }
        for iface_name, net_io in self.net_io.items():
            if iface and iface_name != iface:
                continue
            total['rec_bytes'] += net_io.rec_bytes
            total['rec_packets'] += net_io.rec_packets
            total['tra_bytes'] += net_io.tra_bytes
            total['tra_packets'] += net_io.tra_packets
        return total


class MemInfoContext(object):
    PROC_MEMINFO = '/proc/meminfo'

    def __init__(self):
        """cpu user, nice, system, idle, iowait, irq, softirq
        """
        self._meminfo = {}
        with open(self.PROC_MEMINFO) as f:
            line = f.readline()
            while line:
                key, value = line.split()[0:2]
                self._meminfo[key] = int(value)
                line = f.readline()

    @property
    def mem_total(self):
        return self._meminfo['MemTotal:']

    @property
    def mem_free(self):
        return self._meminfo['MemFree:']

    @property
    def cached(self):
        return self._meminfo['Cached:']

    @property
    def buffers(self):
        return self._meminfo['Buffers:']

    @property
    def swap_total(self):
        return self._meminfo['SwapTotal:']

    @property
    def swap_free(self):
        return self._meminfo['SwapFree:']


class CPULine(object):

    def __init__(self, line):
        self.columns = line.split()

    def _get_column(self, index):
        return self.columns[index] if index == 0 else int(self.columns[index])
    
    @property
    def name(self):
        return self._get_column(0)
    
    @property
    def user(self):
        return self._get_column(1)

    @property
    def nice(self):
        return self._get_column(2)

    @property
    def system(self):
        return self._get_column(3)

    @property
    def idle(self):
        return self._get_column(4)
    
    @property
    def iowait(self):
        return self._get_column(5)
    
    @property
    def irq(self):
        return self._get_column(6)

    @property
    def softirq(self):
        return self._get_column(7)

    def total(self):
        return sum(
            list(map(lambda x: int(x), self.columns[1:]))
        )


class ProcStatContext(object):
    PROC_STAT = '/proc/stat'

    def __init__(self):
        """cpu user, nice, system, idle, iowait, irq, softirq
        """
        self._cpuinfo = {}
        with open(self.PROC_STAT) as f:
            line = f.readline()
            while line:
                if line.startswith('cpu'):
                    cpu = CPULine(line)
                    self._cpuinfo[cpu.name] = cpu
                line = f.readline()

    def get(self, name):
        return self._cpuinfo.get(name)

    def get_total(self, name):
        return self._cpuinfo.get(name).total()

    def get_cpu_list(self):
        return filter(
            lambda x: x != 'cpu', self._cpuinfo.keys()
        )

    def get_cpu_num(self):
        return len(self.get_cpu_list())


class DiskStatsLine(object):

    def __init__(self, line):
        self.columns = line.split()

    def _get_column(self, index):
        return self.columns[index] if index == 2 else int(self.columns[index])
    
    @property
    def major_num(self):
        return self._get_column(0)
    
    @property
    def minor_num(self):
        return self._get_column(1)

    @property
    def dev_name(self):
        return self._get_column(2)

    @property
    def reads_completed(self):
        return self._get_column(3)

    @property
    def writes_completed(self):
        return self._get_column(8)

    @property
    def sectors_read(self):
        return self._get_column(5)

    @property
    def sectors_write(self):
        return self._get_column(9)


class DiskStatsContext(object):
    PROC_DISKSTATS = '/proc/diskstats'
    SYS_BLOCK = '/sys/block'
    VIRTUAL_BLOCK = '/sys/devices/virtual/block'

    def __init__(self, sector_size=512):
        """cpu user, nice, system, idle, iowait, irq, softirq
        """
        self._blocks = self._get_blocks()
        self.sector_size = sector_size
        self.disk_stats = {}
        lines = []
        with open(self.PROC_DISKSTATS) as f:
            lines = f.readlines()
        for line in lines:
            disk_stats_line = DiskStatsLine(line)
            self.disk_stats[disk_stats_line.dev_name] = disk_stats_line

    def _get_blocks(self):
        return set(os.listdir(self.SYS_BLOCK)) - set(os.listdir(self.VIRTUAL_BLOCK))

    def get(self, name):
        return self.disk_stats.get(name)

    def get_read_bytes(self, dev_name=None):
        sectors_read = 0
        if dev_name:
            sectors_read += self.get(dev_name).sectors_read
        else:
            for dev_name, disk_stats in self.disk_stats.items():
                if dev_name not in self._blocks:
                    continue
                sectors_read += disk_stats.sectors_read
        return sectors_read * self.sector_size

    def get_write_bytes(self, dev_name=None):
        sectors_write = 0
        if dev_name:
            sectors_write += self.get(dev_name).sectors_write
        else:
            for dev_name, disk_stats in self.disk_stats.items():
                if dev_name not in self._blocks:
                    continue
                sectors_write += disk_stats.sectors_write
        return sectors_write * self.sector_size


"""
Example
# /etc/fstab
# Created by anaconda on Sat Dec 21 18:48:39 2019
#
# Accessible filesystems, by reference, are maintained under '/dev/disk'
# See man pages fstab(5), findfs(8), mount(8) and/or blkid(8) for more info
#
/dev/mapper/centos-root /                       xfs     defaults        0 0
UUID=e7d3d212-29da-4184-bda2-5efa3c602c9e /boot                   xfs     defaults        0 0
/dev/mapper/centos-home /home                   xfs     defaults        0 0
/dev/mapper/centos-swap swap                    swap    defaults        0 0
[root@host-xx Agent]# 

"""

class FSTabLine(object):

    def __init__(self, line):
        self._columns = line.split()

    @property
    def fs_spec(self):
        return self._columns[0]

    @property
    def fs_file(self):
        return self._columns[1]

    @property
    def fs_vfstype(self):
        return self._columns[2]

    @property
    def fs_mntops(self):
        return self._columns[3]

    @property
    def fs_freq(self):
        return int(self._columns[4])

    @property
    def fs_passno(self):
        return int(self._columns[5])


class FSTab(object):
    ETC_FSTAB = '/etc/fstab'
    SKIP_TYPES = ['swap', 'none']

    def __init__(self):
        self.fstab_map = {}
        with open(self.ETC_FSTAB) as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fs_table = FSTabLine(line)
            if fs_table.fs_vfstype in self.SKIP_TYPES:
                continue
            self.fstab_map[fs_table.fs_file] = fs_table

    def get_fs_files(self):
        return self.fstab_map.keys()

    def get(self, fs):
        return self.fstab_map.get(fs)
