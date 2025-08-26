from abc import ABCMeta, abstractmethod


# compatibility to python 2 & 3
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests


class SixgillBaseRequest(object):
    __metaclass__ = ABCMeta
    SIXGILL_API_BASE_URL = 'https://api.cybersixgill.com/'

    def __init__(self, channel_id, *args, **kwargs):
        self.request = requests.Request(self.method, **kwargs)
        self.request.headers['Cache-Control'] = 'no-cache'
        self.request.headers['X-Channel-Id'] = channel_id

    @property
    @abstractmethod
    def end_point(self):
        pass

    @property
    @abstractmethod
    def method(self):
        pass

    def _get_url(self):
        return urljoin(self.SIXGILL_API_BASE_URL, self.end_point)

    def prepare(self):
        self.request.url = self._get_url()
        return self.request.prepare()
