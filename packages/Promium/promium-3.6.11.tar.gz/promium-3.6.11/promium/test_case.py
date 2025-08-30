import contextlib
import errno
import os
import signal
import threading
import urllib.parse

import urllib3
import pytest
import logging
import traceback

from urllib.parse import urlsplit
from functools import wraps
from selenium.common.exceptions import WebDriverException

from promium.assertions import (
    WebDriverSoftAssertion,
    RequestSoftAssertion
)
from promium.exceptions import PromiumException
from promium.browsers import (
    FirefoxBrowser, ChromeBrowser, OperaBrowser, RemoteBrowser
)
from promium.logger import (
    request_logging,
    logger_for_loading_page
)


TEST_PROJECT = os.environ.get('TEST_PROJECT')
TEST_CASE = os.environ.get('TEST_CASE')

log = logging.getLogger(__name__)

DRIVERS = {
    'firefox': 'Firefox',
    'chrome': 'Chrome',
    'safari': 'Safari',
    'opera': 'Opera',
    'ie': 'Ie',
}

MAX_LOAD_TIME = 10


DEFAULT_HEADERS = {
    "Accept-Encoding": 'gzip, deflate',
    "Accept": "*/*",
    "Connection": "keep-alive",
}


def timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if threading.current_thread() is threading.main_thread():
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator


@timeout(300)
def create_driver(
        device, proxy_server=None, env_var='SE_DRIVER', default='chrome://',
        browser_options=None,
):
    """
    Examples:

        - 'chrome://'
        - 'firefox://'
        - 'opera://'

    """
    driver_options = {
        "device": device,
        "proxy_server": proxy_server,
        "is_headless": os.environ.get("HEADLESS") == "Enabled",
    }
    if browser_options and 'chrome' in browser_options.__module__:
        driver_options["browser_options"] = browser_options

    driver_dsn = os.environ.get(env_var) or default

    if not driver_dsn:
        raise RuntimeError(f'Selenium WebDriver is not set in the {env_var} '
                           f'environment variable')
    try:
        scheme, netloc, url, _, _ = urlsplit(driver_dsn)
    except ValueError as e:
        raise ValueError(f'Invalid url: {driver_dsn}') from e

    if scheme in DRIVERS:
        if scheme == "chrome":
            return ChromeBrowser(**driver_options)
        elif scheme == "firefox":
            return FirefoxBrowser(device=device)
        elif scheme == "opera":
            return OperaBrowser(device=device)
        else:
            raise ValueError(f'Unknown client specified: {scheme}')

    elif scheme.startswith('http+'):
        proto, _, client = scheme.partition('+')
        if not netloc:
            raise ValueError(f'Network address is not specified: {driver_dsn}')

        if client not in DRIVERS:
            raise ValueError(f'Unknown client specified: {client}')

        driver_options["client"] = client
        driver_options["hub"] = f'{proto}://{netloc}{url}'

        try:
            driver = RemoteBrowser(**driver_options)
        except WebDriverException:
            log.warning("Second attempt for remote driver connection.")
            driver = RemoteBrowser(**driver_options)
        except KeyError as e:
            log.warning(str(e))
            if "status" in str(e):
                raise PromiumException(
                    "Session timed out because the browser was idle too long."
                    "Or no free slots for create new session."
                ) from e
            raise
        return driver

    raise ValueError(f'Unknown driver specified: {driver_dsn}')


class TDPException(Exception):

    def __init__(self, *args):
        self.message = (
            "exception caught during execution test data preparing.\n"
            "Look at the original traceback:\n\n%s\n"
        ) % ("".join(traceback.format_exception(*args)))

    def __str__(self):
        return self.message


class TDPHandler:
    """
    TDP - Test Data Preparation
    context manager for handling any exception
    during execution test data preparing.
    We need to raise a specific custom exceptions.
    :example:
    with self.tdp_handler():
        some code
    """

    def __init__(self):
        pass

    def __enter__(self):
        log.info("[TDP] Start test data preparing...")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        log.info("[TDP] Finish test data preparing")
        if exc_type:
            raise TDPException(exc_type, exc_value, exc_tb)
        return


class TestCase(object):
    xrequestid = None
    test_case_url = None
    assertion_errors = None
    proxy_server = None

    def tdp_handler(self):
        """
        Use this context manager for prepare of test data only,
        not for business logic!
        """
        return TDPHandler()

    def setup_method(self, method):
        check_test_case = os.environ.get("TEST_CASE")
        if check_test_case == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")


@pytest.mark.usefixtures("driver_init")
class WebDriverTestCase(TestCase, WebDriverSoftAssertion):
    driver = None

    @logger_for_loading_page
    def get_url(self, url, cleanup=True):
        log.info(f'Open Page: {url}')
        self.driver.get(url)
        if cleanup:
            with contextlib.suppress(WebDriverException):
                self.driver.execute_script('localStorage.clear()')
        return url


@pytest.mark.usefixtures("request_init")
class RequestTestCase(TestCase, RequestSoftAssertion):
    session = None

    def get_response(
        self, url, method="GET", timeout=10, cookies=None, **kwargs,
    ):
        self.session.url = url
        self.session.status_code = None
        session = self.session
        request_cookies = {'xrequestid': self.xrequestid}
        if cookies:
            request_cookies.update(cookies)
        cookies_str = '; '.join(
            [f'{k}={v}' for k, v in request_cookies.items()]
        )

        if hasattr(self.session, 'session_cookie'):
            cookies_str += f'; {self.session.session_cookie}'

        if self.proxy_server and not hasattr(session, 'proxy_override_session'):
            session = urllib3.ProxyManager(
                proxy_url=f"http://{self.proxy_server}",
                cert_reqs=False,
                timeout=15,
            )
            session.proxy_override_session = True

        headers = DEFAULT_HEADERS
        headers['Cookie'] = cookies_str
        if new_headers := kwargs.pop('headers', None):
            headers.update(new_headers)

        for i in range(1, 3):
            response = session.request(
                url=url,
                method=method,
                headers=headers,
                timeout=urllib3.Timeout(
                    connect=5.0,
                    read=float(timeout),
                    total=float(timeout),
                ),
                **kwargs,
            )
            request_logging(response, url, method, **kwargs)
            self.session.status_code = response.status
            response.status_code = response.status
            if (
                    response.status in [502, 503, 504] and
                    method in ["POST", "GET"]
            ):
                log.warning(
                    f'[Request Retry]: attempt:{i}, '
                    f'status: {response.status}'
                )
            else:
                cookies = response.headers.get("set-cookie")
                if hasattr(self.session, 'session_cookie'):
                    self.session.session_cookie += f'; {cookies}'
                else:
                    self.session.session_cookie = cookies
                break

        # fix display full url
        parser = urllib.parse.urlparse(url)
        if hasattr(response, 'url') and response.url:
            if not response.url.startswith('http') and 'http' in parser.scheme:
                response.url = (
                    f'{parser.scheme}://{parser.netloc}{response.url}'
                )

        return response
