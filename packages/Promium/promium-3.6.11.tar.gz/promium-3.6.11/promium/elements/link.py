
import urllib3
import logging

from promium.base import Element
from promium.helpers import ParseUrl


log = logging.getLogger(__name__)


class Link(Element):

    @property
    def href(self):
        return self.get_attribute("href")

    @property
    def parse_url(self):
        """
        Using parse_url to parse href. Can get attributes:
        - scheme
        - host
        - sub_domain
        - port
        - path
        - params
        - query
        - fragment
        - product_id
        """
        return ParseUrl(self.href)

    @property
    def response(self):
        """Get url response"""
        http = urllib3.PoolManager(
            cert_reqs=False,
            timeout=5,
        )
        cookies_str = '; '.join([
            f'{cookie["name"]}={cookie["value"]}'
            for cookie in self.driver.get_cookies()
        ])
        for i in range(1, 3):
            r = http.request(
                url=self.href,
                method='GET',
                headers={
                    "Accept-Encoding": 'gzip, deflate',
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                    "Cookie": cookies_str,
                },
            )
            if r.status in [502, 503, 504]:
                log.warning(f'[Request Retry]: attempt:{i}, status: {r.status}')
            else:
                break

        return r

    @property
    def get_status_code(self):
        """Gets status response code from link"""
        return self.response.status
