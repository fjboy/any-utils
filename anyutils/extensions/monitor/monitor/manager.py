import logging
import importlib
import platform

DRIVER_TYPE_AUTO = 0
DRIVER_TYPE_BASHDRIVER = 1
DRIVER_TYPE_PSUTILDRIVER = 2

LOG = logging.getLogger(__name__)


class HostMonitoryManager(object):
    DRIVER_MAP = {
        DRIVER_TYPE_BASHDRIVER: ('bashdriver', 'HostMonitorBashDriver'),
        DRIVER_TYPE_PSUTILDRIVER: ('psutildriver', 'HostMonitorPsutilDriver'),
    }

    @classmethod
    def get_host_monitor_driver(cls, driver=DRIVER_TYPE_AUTO):
        monitor_mod, monitor_cls = None, None
        if driver == DRIVER_TYPE_AUTO:
            os_name = platform.platform()
            LOG.warning('os is %s', os_name)
            if os_name.lower().startswith('windows'):
                driver = cls.DRIVER_MAP[DRIVER_TYPE_PSUTILDRIVER]
            else:
                driver = cls.DRIVER_MAP[DRIVER_TYPE_BASHDRIVER]
            try:
                monitor_mod, monitor_cls = driver[0], driver[1]
                importlib.import_module(
                    '.{0}'.format(monitor_mod), 'monitor.host')
            except ImportError:
                raise Exception('get host monitor driver failed, '
                                'please install psutil')
        else:
            driver = cls.DRIVER_MAP[driver]
            monitor_mod, monitor_cls = driver[0], driver[1]
        module = importlib.import_module(
            '.{0}'.format(monitor_mod), 'monitor.host')
        return getattr(module, monitor_cls)
