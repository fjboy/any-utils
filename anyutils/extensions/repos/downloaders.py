"""wallpaper downloader"""

import importlib
import os

try:
    from urllib import parse as urlparse
except ImportError:
    urlparse = importlib.import_module('urlparse')

from anycode.common import cliparser
from anycode.common import log
from anycode import system



LOG = log.getLogger(__name__)

UHD_CHOICES = ['only', 'include', 'no']
RESOLUTION_UHD = 'uhd'
RESOLUTION_1920 = '1920x1080'
UHD_CHOICES = ['only', 'include', 'no']
UHD_RESOLUTION_MAPPING = {'include': None,
                          'no': RESOLUTION_1920,
                          'only': RESOLUTION_UHD}

DOWNLOADER = {
    'yum': 'anyutils.extensions.repos.yum.YumRepoDownloader'
}


class RepoDownload(cliparser.CliBase):
    NAME = 'repo-download'
    ARGUMENTS = [
        cliparser.Argument('url',
                           help='The url of repo'),
        cliparser.Argument('-w', '--workers', type=int, default=10,
                           help='the num download workers, default is 10'),
        cliparser.Argument('-t', '--timeout', type=int, default=300,
                           help='timeout, default is 300s'),
        cliparser.Argument('-s', '--save',
                           help='the directory to save'),
        cliparser.Argument('-n', '--no-progress', action='store_true',
                           help='do not show progress'),
        cliparser.Argument('--wget', action='store_true', help='use wget'),
    ]

    def __call__(self, args):
        if args.wget and system.OS.is_windows():
            LOG.error('Wget is not support in this os')
            return 1

        mod, _, klass = DOWNLOADER['yum'].rpartition('.')
        module = importlib.import_module(mod)
        manager_cls = getattr(module, klass)
        url = args.url.endswith('/') and args.url[:-1] or args.url
        if not args.save:
            save_dir = os.path.basename(urlparse.urlsplit(url).path)
        else:
            save_dir = args.save
        manager = manager_cls(progress=not args.no_progress,
                              download_dir=save_dir, workers=args.workers,
                              timeout=args.timeout, use_wget=args.wget)
        manager.download(args.url.endswith('/') and args.url[:-1] or args.url)


def list_sub_commands():
    return [RepoDownload]
