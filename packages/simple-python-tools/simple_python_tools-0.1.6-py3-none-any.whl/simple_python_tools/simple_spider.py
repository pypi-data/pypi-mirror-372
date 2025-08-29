from bs4 import BeautifulSoup
from abc import ABCMeta, abstractmethod

from . import simple_logger as logger
from . import simple_requests as requests

class SimpleSpider():
    def __init__(self, HOME_URL: str):
        self.HOME_URLS = [HOME_URL]

    def __init__(self, HOME_URLS: list[str]):
        self.HOME_URLS = HOME_URLS

class SimpleBlockedSpider(SimpleSpider):
    @abstractmethod
    def _get_possible_home_links(self, soup: BeautifulSoup) -> list[str]:
        pass

    def _get_home_links(self):
        logger.debug('Getting home links from', self.PUBLICATION_URL)
        res = requests.get(self.PUBLICATION_URL)
        if res is None or res.status_code != 200:
            logger.warning(f'Get presentation page {self.PUBLICATION_URL} failed')
            return []
        
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, features='html.parser')

        test_links = self._get_possible_home_links(soup)
        logger.debug(test_links)
        return test_links

    def _get_available_home_links(self):
        home_links = self._get_home_links()
        logger.info('Find possible home links:', ', '.join(home_links))
        home_urls = []
        for home_link in home_links:
            http_home_link = home_link.replace('https', 'http')
            if requests.is_available(http_home_link):
                logger.info(f'Detect {http_home_link} available')
                home_urls.append(http_home_link)
            else:
                logger.info(f'Detect {http_home_link} NOT available')

        return home_urls

    def __init__(self, PUBLICATION_URL: str):
        self.PUBLICATION_URL = PUBLICATION_URL
        self.HOME_URLS = self._get_available_home_links()