import os
import datetime
import logging
import urllib3
from collections import namedtuple

import pytest
import allure

from selenium.common.exceptions import WebDriverException
from promium.test_case import create_driver
from promium.common import upload_screenshot
from promium.device_config import CHROME_DESKTOP_1920_1080, DesktopDevice
from promium.logger import Logger
from promium.exceptions import BrowserConsoleException, PromiumException


log = logging.getLogger(__name__)

FailInfoSelenium = namedtuple('FailInfoSelenium', [
    'test_type', 'url', 'screenshot', 'test_case', 'run_command', 'txid'
])
FailInfoRequest = namedtuple('FailInfoRequest', [
    'test_type', 'url', 'test_case', 'status_code', 'run_command', 'txid'
])

DEFAULT_HEADERS = {
    "Accept-Encoding": 'gzip, deflate',
    "Accept": "*/*",
    "Connection": "keep-alive",
}


@pytest.hookimpl
def pytest_addoption(parser):
    parser.addoption(
        "--capturelog",
        dest="logger",
        default=None,
        action="store_true",
        help="Show log messages for each failed test"
    )
    parser.addoption(
        "--fail-debug-info",
        action="store_true",
        help="Show screenshot and test case urls for each failed test"
    )
    parser.addoption(
        "--duration-time",
        action="store_true",
        help="Show the very slow test"
    )
    parser.addoption(
        "--allure-report",
        action="store_true",
        help="Generate allure report"
    )
    parser.addoption(
        "--highlight",
        action="store_true",
        help="Highlighting elements"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Enable headless mode for Chrome browser only"
    )
    parser.addoption(
        "--chrome",
        action="store_true",
        help="Use chrome browser"
    )
    parser.addoption(
        "--firefox",
        action="store_true",
        help="Use firefox browser"
    )
    parser.addoption(
        "--opera",
        action="store_true",
        help="Use opera browser"
    )
    parser.addoption(
        "--repeat",
        action="store",
        default=1,
        type=int,
        metavar='repeat',
        help='Number of times to repeat each test. Mostly for debug purposes'
    )
    parser.addoption(
        "--check-console",
        action="store_true",
        help="Check browser console js and other errors"
    )
    parser.addoption(
        "-R",
        "--replace-headless",
        action="store",
        help=(
            """ When selenium tests running in Chrome Headless mode,
            the Headless browser can recognized as a bot,
            so we change the agent's username to a real one.
            By default user agent contains something like
            "HeadlessChrome/86.0.4240.75", but we need "Chrome/86.0.4240.75"
            You need to specify the Chrome version. """
        )
    )


@pytest.fixture()
def request_init(request):

    def _get_fail_debug(request):
        """Failed test report generator"""
        if hasattr(request.config, "get_failed_test_command"):
            run_command = request.config.get_failed_test_command(request)
        else:
            run_command = "Please, add run command in your fixture."

        session = request.cls.session
        if session and not hasattr(session, 'status_code'):
            session.status_code = None

        return FailInfoRequest(
            test_type='request',
            url=(session.url, [None])[0],
            test_case=(request.cls.test_case_url, [None])[0],
            status_code=(session.status_code, [None])[0],
            run_command=(run_command, [None])[0],
            txid=(request.cls.xrequestid, [None])[0],
        )

    session = urllib3.PoolManager(
        cert_reqs=False,
        timeout=15,
        headers=DEFAULT_HEADERS,
    )
    session.url = (
        'Use self.get_response(url) for request tests or '
        'util methods for api tests!'
    )
    request.cls.session = session
    request.config.get_fail_debug = _get_fail_debug
    request.config.assertion_errors = request.cls.assertion_errors = []
    yield session
    request.cls.xrequestid = None


@pytest.fixture()
def driver_init(request):
    def _get_screenshot_png():
        try:
            return driver.get_screenshot_as_png()
        except Exception as e:
            log.error(f'[PROMIUM] Have problem with make screenshot: {e}')
            return 'Error'

    def _get_fail_debug(request):
        """Failed test report generator"""
        driver = request.config.driver

        alerts = 0
        try:
            while driver.switch_to.alert:
                alert = driver.switch_to.alert
                print('Unexpected ALERT: %s\n' % alert.text)
                alerts += 1
                alert.dismiss()
        except Exception:
            if alerts != 0:
                print('')
        try:
            url = driver.current_url
        except Exception as e:
            url = str(e)
        screenshot = upload_screenshot(driver)

        if hasattr(request.config, "get_failed_test_command"):
            run_command = request.config.get_failed_test_command(request)
        else:
            run_command = "Please, add run command in your fixture."

        return FailInfoSelenium(
            test_type='selenium',
            url=(url, [None])[0],
            screenshot=(screenshot, [None])[0],
            test_case=(request.cls.test_case_url, [None])[0],
            run_command=(run_command, [None])[0],
            txid=(request.cls.xrequestid, [None])[0],
        )

    def _is_skipped_error(request, error):
        for msg in request.cls.excluded_browser_console_errors:
            if msg["msg"] in error and msg["comment"]:
                return True
        return False

    def _check_console_errors(request):
        driver = request.config
        if hasattr(driver, "console_errors"):
            if driver.console_errors:
                browser_console_errors = driver.console_errors
                if hasattr(request.cls, "excluded_browser_console_errors"):
                    if request.cls.excluded_browser_console_errors:
                        try:
                            return list(filter(
                                lambda err: not _is_skipped_error(
                                    request, err),
                                browser_console_errors
                            ))
                        except Exception as e:
                            raise PromiumException(
                                "Please check your excluded errors list. "
                                "Original exception is: %s" % e
                            )
                return browser_console_errors
        return []

    mark = request.node.get_closest_marker('device')
    device = mark.args[0] if mark else CHROME_DESKTOP_1920_1080
    replacement_version = request.config.getoption('--replace-headless')
    if hasattr(device, "user_agent") and replacement_version:
        if not device.user_agent and "chrome" in os.environ.get("SE_DRIVER"):
            user_agent = (
                f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) "
                f"Chrome/{replacement_version} Safari/537.36"
            )
            device = DesktopDevice(1920, 1080, user_agent)

    request.cls.device = device
    if hasattr(request.config, "proxy_server"):
        proxy_server = request.config.proxy_server
    else:
        proxy_server = None
    browser_options = getattr(request.config, "browser_options", None)
    driver = create_driver(
        device,
        proxy_server=proxy_server,
        browser_options=browser_options,
    )
    driver.xrequestid = request.cls.xrequestid
    request.cls.driver = request.config.driver = driver
    request.config.get_fail_debug = _get_fail_debug
    request.config.get_screenshot_png = _get_screenshot_png
    request.config.check_console_errors = _check_console_errors
    request.config.assertion_errors = request.cls.assertion_errors = []
    request.config.console_errors = driver.console_errors = []
    yield driver
    driver.xrequestid = request.cls.xrequestid = None
    request.config.console_errors = driver.console_errors = []
    try:
        driver.close()
        driver.quit()
    except WebDriverException as e:
        log.error(f"[PROMIUM] Original webdriver exception: {e}")


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat > 1:
        metafunc.fixturenames.append('repeat')
        metafunc.parametrize('repeat', range(metafunc.config.option.repeat))


@pytest.fixture(autouse=True)
def logger(request):
    return logging.getLogger()


@pytest.mark.trylast
def pytest_runtest_call(item):
    if hasattr(item.config, "assertion_errors"):
        if item.config.assertion_errors:
            separator = '-' * 46
            assertion_errors_list = f"{separator}\n".join(
                item.config.assertion_errors
            )
            msg = f"\n{separator}\n{assertion_errors_list}{separator}\n"
            raise AssertionError(msg)

    if item.config.getoption("--check-console"):
        if hasattr(item.config, "check_console_errors"):
            browser_console_errors = item.config.check_console_errors(item)
            if browser_console_errors:
                msg = (
                    "Browser console js errors found:"
                    "\n{console_errors}\n".format(
                        console_errors="\n".join(
                            browser_console_errors
                        )
                    )
                )
                raise BrowserConsoleException(msg)


@pytest.mark.tryfirst
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """pytest failed test report generator"""
    outcome = yield
    report = outcome.get_result()
    when = report.when
    item.config.path_to_test = f'{item.location[0]} -k "{item.name}"'

    if when == "call" and not report.passed:
        if item.config.getoption("--fail-debug-info"):
            fail_info = "Fail info not found."
            try:
                if hasattr(item.config, "get_fail_debug"):
                    fail_debug = item.config.get_fail_debug(item)
                    if fail_debug.test_type == 'selenium':
                        fail_info = (
                            (
                                "\nURL: {url}"
                                "\nTEST CASE: {test_case}"
                                "\nSCREENSHOT: {screenshot}"
                                "\nRUN_COMMAND: {run_command}"
                                "\nTXID: {txid}"
                            ).format(
                                url=fail_debug.url,
                                screenshot=fail_debug.screenshot,
                                test_case=fail_debug.test_case,
                                run_command=fail_debug.run_command,
                                txid=fail_debug.txid
                            )
                        )
                        if item.config.getoption("--allure-report"):
                            allure.attach(
                                item.config.get_screenshot_png(),
                                name='SCREENSHOT',
                                attachment_type=allure.attachment_type.PNG,
                            )

                    elif fail_debug.test_type == 'request':
                        fail_info = (
                            "\nURL: {url}"
                            "\nTEST_CASE: {test_case}"
                            "\nSTATUS_CODE: {status_code}"
                            "\nRUN_COMMAND: {run_command}"
                            "\nTXID: {txid}"
                        ).format(
                            url=fail_debug.url,
                            test_case=fail_debug.test_case,
                            status_code=fail_debug.status_code,
                            run_command=fail_debug.run_command,
                            txid=fail_debug.txid
                        )
                    if item.config.getoption("--allure-report"):
                        if fail_debug.test_case:
                            for url in fail_debug.test_case.split():
                                allure.dynamic.link(url=url, name='TestCase')
                        allure.attach(
                            fail_debug.url, name='URL',
                            attachment_type=allure.attachment_type.URI_LIST,
                        )
                        allure.attach(
                            f"""<button onclick="navigator.clipboard.writeText(
                            '{fail_debug.run_command.replace('"', '&quot;')}');
                            this.textContent='Copied';">Copy</button> <br>
                            <div style="font-family: monospace,serif;
                            font-size: 14px;">{fail_debug.run_command}</div>""",
                            name='RUN COMMAND',
                            attachment_type=allure.attachment_type.HTML,
                        )

            except WebDriverException as e:
                fail_info = (
                    "\nWebdriver instance must have crushed: {msg}".format(
                        msg=e.msg
                    )
                )
            finally:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    longrepr.sections.insert(
                        0, ("Captured stdout %s" % when, fail_info, "-")
                    )

        if item.config.getoption("--duration-time"):
            duration = call.stop - call.start
            if duration > 120:
                report.sections.append((
                    "Captured stdout %s" % when,
                    ("\n\n!!!!! The very slow test. "
                     "Duration time is %s !!!!!\n\n")
                    % datetime.datetime.fromtimestamp(duration).strftime(
                        "%M min %S sec"
                    )
                ))


def pytest_configure(config):
    os.environ['PYTHONWARNINGS'] = (
        'ignore:An HTTPS request has been made, '
        'ignore:A true SSLContext object is not available, '
        'ignore:Unverified HTTPS request is being made'
    )

    if config.getoption('--headless'):
        os.environ['HEADLESS'] = 'Enabled'
    if config.getoption("--highlight"):
        os.environ['HIGHLIGHT'] = 'Enabled'
    if config.getoption("--capturelog"):
        config.pluginmanager.register(Logger(), "logger")
    if config.getoption("--check-console"):
        os.environ['CHECK_CONSOLE'] = 'Enabled'
    if not getattr(config, "lastfailed_file", None):
        config.lastfailed_file = "lastfailed"
