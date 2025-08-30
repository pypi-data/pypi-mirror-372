import base64
import os
import datetime

import allure
import urllib3
import json
import time
import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from promium.waits import (
    wait_for_animation, enable_jquery, wait_until_new_window_is_opened
)


log = logging.getLogger(__name__)


http = urllib3.PoolManager(
    cert_reqs=False,
    timeout=5,
)


SCREENSHOT_SERVER_HOST = os.environ.get("SCREENSHOT_SERVER_HOST")
SCREENSHOT_SERVER_LOGIN = os.environ.get("SCREENSHOT_SERVER_LOGIN")
SCREENSHOT_SERVER_PASSWORD = os.environ.get("SCREENSHOT_SERVER_PASSWORD")


def scroll_to_bottom(driver):
    """Scrolls down page"""
    enable_jquery(driver)
    driver.execute_script('jQuery("img.img-ondemand").trigger("appear");')
    driver.execute_script(
        """
        var f = function(old_height) {
            var height = $$(document).height();
            if (height == old_height) return;
            $$('html, body').animate({scrollTop:height}, 'slow', null,
            setTimeout(function() {f(height)}, 1000)
            );
        }
        f();
        """
    )
    wait_for_animation(driver)


def scroll_to_top(driver):
    """Scrolls to the top of the page"""
    enable_jquery(driver)
    driver.execute_script(
        """jQuery('html, body').animate({scrollTop: 0 }, 'slow', null);"""
    )
    wait_for_animation(driver)


def scroll_to_bottom_in_block(driver, element_class):
    """Scrolls to the bottom of the current block"""
    enable_jquery(driver)
    script = """
        var elem = '.'.concat(arguments[0]);
        $(elem).animate({scrollTop: $(elem).prop('scrollHeight')}, 1000);
    """
    driver.execute_script(script, element_class)
    wait_for_animation(driver)


def scroll_to_element(driver, element, base_element=None):
    """
    use base_element if you need for example scroll into popup,
    base_element must be a popup locator.
    """
    enable_jquery(driver)
    if base_element is None:
        base_element = 'html, body'
    script = """
        var elem = arguments[0];
        var base = arguments[1];
        var relativeOffset = (
            jQuery(elem).offset().top - jQuery(base).offset().top
        );
        jQuery(base).animate({
            scrollTop: relativeOffset
            }, 'slow', null
        );
             """
    driver.execute_script(script, element, base_element)
    wait_for_animation(driver)


def scroll_with_offset(driver, element, with_offset=0):
    """
    Adjusting the final scroll position by adding or subtracting a
    specified number of pixels
    """
    enable_jquery(driver)
    script = """
        var elem = arguments[0];
        jQuery('html, body').animate({
            scrollTop: jQuery(elem).offset().top + arguments[1]
            }, 'fast', null
        );
        """
    driver.execute_script(script, element, with_offset)
    wait_for_animation(driver)


def scroll_into_end(driver):
    """Scroll block into end page"""
    enable_jquery(driver)
    driver.execute_script(
        'window.scrollTo(0, document.body.scrollHeight);'
    )
    wait_for_animation(driver)


def open_link_in_new_tab(driver, url=None):
    """
    Opening URL in new tab and switches to recently opened window
    If URL is None - an empty window will open
    """
    main_window = driver.current_window_handle
    driver.execute_script(
        f'''window.open("{
        "about:blank" if url is None else url
        }","_blank");'''
    )
    new_window = wait_until_new_window_is_opened(driver, main_window)
    switch_to_window(driver, new_window)


def switch_to_window(driver, window_handle):
    """Switches to window"""
    driver.switch_to.window(window_handle)


def get_screenshot_path(name, with_date=True):
    now = datetime.datetime.now().strftime('%d_%H_%M_%S_%f')
    screenshot_name = f"{name}_{now}.png" if with_date else f"{name}.png"
    screenshots_folder = "/tmp"
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    screenshot_path = os.path.join(screenshots_folder, screenshot_name)
    return screenshot_path, screenshot_name


def if_server_have_problem():
    try:
        r = http.request(
            url=f"https://{SCREENSHOT_SERVER_HOST}",
            method='GET',
            headers={
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive',
            },
        )
        assert r.status <= 400, f'Have problem {r.status}: {r.reason}'
        return False
    except Exception as e:
        return str(e)


def _upload_to_server(screenshot_path, screenshot_name):

    status_server = if_server_have_problem()
    if status_server:
        return status_server

    def read_in_chunks(img, block_size=1024, chunks=-1):
        """
        Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k.
        """
        while chunks:
            data = img.read(block_size)
            if not data:
                break
            yield data
            chunks -= 1

    screenshot_url = f"https://{SCREENSHOT_SERVER_HOST}/{screenshot_name}"
    r = http.request(
        url=screenshot_url,
        method='PUT',
        headers={
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(
                f'{SCREENSHOT_SERVER_LOGIN}:{SCREENSHOT_SERVER_PASSWORD}'
                ''.encode()
            ).decode()
        },
        body=read_in_chunks(open(screenshot_path, 'rb')),
    )
    os.remove(screenshot_path)
    if r.status != 201:
        return (
            f"Screenshot not uploaded to server. "
            f"Status code: {r.status_code}, reason: {r.reason}"
        )
    return screenshot_url


def upload_screenshot(driver, path_name="screenshot", path_with_date=True):
    try:
        screenshot_path, screenshot_name = get_screenshot_path(
            name=path_name,
            with_date=path_with_date
        )
        driver.save_screenshot(screenshot_path)

        if SCREENSHOT_SERVER_HOST:
            return _upload_to_server(screenshot_path, screenshot_name)
        return f"file://{screenshot_path}"

    except Exception as e:
        return f'No screenshot was captured due to exception {repr(e)}'


def control_plus_key(driver, key):
    """Imitations press CONTROL key + any key"""
    (
        ActionChains(driver)
        .key_down(Keys.CONTROL)
        .send_keys(key)
        .key_up(Keys.CONTROL)
        .perform()
    )


def set_local_storage(driver, key, value):
    """Sets value in browsers local storage"""
    driver.execute_script(f"localStorage.setItem('{key}', '{value}')")


def delete_cookie_item(driver, name):
    """Deleting cookie on current page"""
    driver.delete_cookie(name)
    driver.refresh()


def delete_element_from_dom(driver, element):
    """Removes a specific DOM element from the webpage"""
    enable_jquery(driver)
    driver.execute_script(f"""
        var element = document.querySelector("{element}");
        if (element)
        element.parentNode.removeChild(element);
    """)


def find_network_log(
        driver, find_mask, find_status=200, timeout=5, find_type=None
):
    """ find xrh response and request data from browser network logs
    :param driver: selenium driver
    :param find_mask: find word in request url
    :param find_status: find response with this status
    :param timeout: tries
    :param find_type: check type request in network (example find_type='Fetch')
    :return: [{response, data, body}, {response, data, body}] or []
    """
    def get_log(request_mask):
        found_requests = []
        for performance_log in driver.get_log('performance'):
            # only response logs
            if (
                request_mask in performance_log['message'] and
                'responsereceived' in performance_log['message'].lower()
            ):
                json_log = json.loads(performance_log['message'])['message']
                if not json_log['params'].get('response'):
                    continue
                response = json_log['params']['response']
                if (
                    response['status'] == find_status and (
                        not find_type or json_log['params']['type'] == find_type
                    )
                ):
                    found_requests.append(json_log)
        return found_requests

    while timeout >= 0:
        xhr_log = get_log(find_mask)
        if xhr_log:
            break
        time.sleep(0.5)
        timeout -= 1

    result_all_logs = []
    for network_log in xhr_log:
        requestId = network_log['params']['requestId']  # noqa: N806
        response = network_log['params']['response']
        try:
            request_data = driver.execute_cdp_cmd(
                'Network.getRequestPostData', {'requestId': requestId}
            )
            request_data = json.loads(request_data['postData'])
        except Exception:
            request_data = None

        try:
            response_body = driver.execute_cdp_cmd(
                'Network.getResponseBody', {'requestId': requestId}
            )
            response_body = json.loads(response_body['body'])
        except Exception:
            response_body = None

        log.info(
            f"[XHR Logs]: find by mask: '{find_mask}' -> {response.get('url')} "
            f"{response.get('status')} - {response.get('statusText')}"
        )
        result_all_logs.append({
            'response': {
                'url': response.get('url'),
                'status': response.get('status'),
                'statusText': response.get('statusText'),
            },
            'data': request_data,
            'body': response_body,
        })

    allure.attach(
        name=f"[XHR log] '{find_mask}', status:{find_status}, type:{find_type}",
        body=json.dumps(result_all_logs, indent=4, ensure_ascii=False),
        attachment_type=allure.attachment_type.JSON,
    )
    return result_all_logs
