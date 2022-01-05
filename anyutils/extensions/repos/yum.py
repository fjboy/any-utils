import re
import os
import importlib

try:
    from urllib import parse as urlparse
except ImportError:
    urlparse = importlib.import_module('urlparse')

from anycode.common import log
from anycode.downloader.urllib import driver as urllib_driver

LOG = log.getLogger(__name__)

DRIVERS = {
    'wget': 'anycode.downloader.wget.driver.WgetDriver',
    'urllib3': 'anycode.downloader.urllib.driver.Urllib3Driver'
}


class YumRepoDownloader(object):

    def __init__(self, use_wget=False, workers=None,
                 timeout=None, download_dir=None, progress=False):
        self.workers = workers or 1
        self.timeout = timeout
        self.download_dir = download_dir or './'
        self.driver_name = 'wget' if use_wget else 'urllib3'
        self.progress = progress
        self._driver = None
        self.default_headers = {}

    def get_download_driver(self, download_dir=None):
        if not self._driver:
            mod, _, klass = DRIVERS.get(self.driver_name).rpartition('.')
            driver_cls = getattr(importlib.import_module(mod), klass)
            self._driver = driver_cls(
                download_dir=download_dir or self.download_dir,
                timeout=self.timeout, workers=self.workers,
                progress=self.progress)
        return self._driver

    def download(self, url):
        """Download images found in page

        page : int
            the page number of bingimg web pages
        resolution : string, optional
            the resolution of image to download, by default None
        threads : int, optional
            download threads, if None, save, by default None
        progress : bool, optional
            show progress, by default False
        """
        repodata, packages = self.get_repo_url(url)
        pack_links = self.find_packages_links(packages)
        LOG.info('found %s packages in: %s.', len(pack_links), url)

        LOG.info('download repodata ...')
        self._download(self.find_repodata_links(repodata),
                       os.path.join(self.download_dir, 'repodata'))

        self._download(self.find_packages_links(packages),
                       os.path.join(self.download_dir, 'Packages'))

    def _download(self, links, save_dir):
        LOG.info('download links, save to %s', save_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        download_driver = self.get_download_driver(download_dir=save_dir)
        download_driver.download_urls(links)

    def get_repo_url(self, url):
        repodata, packages = None, None
        links = urllib_driver.find_links(url, headers=self.default_headers)
        for link in links:
            if link in ['repodata', 'repodata/', '{}/repodata/']:
                repodata = urlparse.urljoin(url + '/', link)
            elif link in ['Packages', 'Packages/', '{}/Packages/']:
                packages = urlparse.urljoin(url + '/', link)
            if repodata and packages:
                break
        if not all([repodata, packages]):
            raise Exception('Invalid yum reppo: {}'.format(url))
        return repodata, packages

    def find_packages_links(self, url):
        link_regex = r'.*\.rpm$'
        links = urllib_driver.find_links(url, link_regex=link_regex,
                                        headers=self.default_headers)
        return [urlparse.urljoin(url, link) for link in links]
    
    def find_repodata_links(self, url):
        links = []
        for link in urllib_driver.find_links(url):
            if re.match(r'/.*|\.\.|https*:|javascript:.*|mailto:.*', link):
                continue
            links.append(urlparse.urljoin(url, link))
        return links
