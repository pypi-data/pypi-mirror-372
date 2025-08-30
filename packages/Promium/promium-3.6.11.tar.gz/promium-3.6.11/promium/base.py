import logging
import os
import random
import time
from collections.abc import Callable, Iterator, Sequence
from functools import wraps
from typing import Any, Self

import pytest
import urllib3
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from promium.common import (
    find_network_log,
    scroll_into_end,
    scroll_to_bottom,
    scroll_to_element,
    scroll_to_top,
    set_local_storage,
    switch_to_window,
)
from promium.exceptions import (
    ElementLocationException,
    LocatorException,
    PromiumException,
)
from promium.expected_conditions import is_present
from promium.logger import (
    add_logger_to_base_element_classes,
    logger_for_loading_page,
)
from promium.waits import (
    wait_document_status,
    wait_for_alert,
    wait_for_alert_is_displayed,
    wait_for_animation,
    wait_for_page_loaded,
    wait_part_appear_in_class,
    wait_part_disappear_in_class,
    wait_until,
    wait_until_new_window_is_opened,
    wait_websocket_connection_open,
)


log = logging.getLogger(__name__)


MAX_TRIES = 20
NORMAL_LOAD_TIME = 10


def with_retries(tries: int, second_to_wait: float) -> Any:
    """
    If element not found wait and try again
    If element found returned
    :param int tries:
    :param float second_to_wait: wait seconds
    :return: callable_func
    """

    def callable_func(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for _ in range(tries):
                res = func(*args, **kwargs)
                if res:
                    return res
                time.sleep(second_to_wait)

            element = args[0]
            raise ElementLocationException(
                f"Element with {element.by}={element.locator} not found"
            )

        return wrapper

    return callable_func


def highlight_element(func: Any) -> Any:
    """
    Enabled for debug only
    :param func:
    :return: wrapper
    """

    @wraps(func)
    def wrapper(self: Any, *args, **kwargs) -> WebElement:
        element = func(self, *args, **kwargs)
        highlight_status = os.environ.get("HIGHLIGHT")
        if highlight_status == "Enabled":
            self.driver.execute_script(
                """
                element = arguments[0];
                original_style = element.getAttribute('style');
                element.setAttribute('style', original_style +
                ";border: 3px solid #D4412B;");
                setTimeout(function(){
                element.setAttribute('style', original_style);
                    }, 300);
                """,
                element,
            )
            time.sleep(0.5)
        return element

    return wrapper


def text_to_be_present_in_element(element: "Element", text_: str) -> Callable:
    def _predicate(driver: WebDriver) -> bool:
        try:
            return text_ in element.lookup().text
        except StaleElementReferenceException:
            return False

    return _predicate


class Page:
    def __init__(
        self, driver: WebDriver, monkeypatch: pytest.MonkeyPatch = None
    ) -> None:
        self._driver = driver
        self.previous_window_handle = self.driver.current_window_handle
        self.monkeypatch = monkeypatch

    url = None

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def is_mobile(self) -> bool:
        """Return True if test run like mobile device"""
        return (
            "mobile"
            in self.driver.execute_script("return navigator.userAgent;").lower()
        )

    @property
    def is_desktop(self) -> bool:
        """Return True if test run like desktop device"""
        return not self.is_mobile

    def lookup(self) -> None:
        return None

    @logger_for_loading_page
    def open(self, **kwargs) -> str:  # noqa A003
        if not self.url:
            raise PromiumException("Can't open page without url")
        start = time.time()
        url = self.url.format(**kwargs)
        log.info(f"Open Page: {url}")
        try:
            self.driver.get(url)
        except TimeoutException:
            log.error(f"[PROMIUM] Page load time: {time.time() - start}")
            raise
        return url

    @logger_for_loading_page
    def refresh(self) -> None:
        self.driver.refresh()

    def wait_for_page_loaded(self) -> None:
        wait_for_page_loaded(self.driver)

    def wait_for_source_changed(self, action_func: Any, *args, **kwargs) -> None:
        """Waiting for status code of current page be changed"""
        source = self.driver.page_source
        action_func(*args, **kwargs)
        wait_until(
            self.driver,
            lambda driver: driver.page_source != source,
            msg="Page source didn't change.",
        )

    def get_status_code(self) -> int:
        """get status_code from current page"""
        http = urllib3.PoolManager(
            cert_reqs=False,
            timeout=5,
        )
        cookies_str = "; ".join([
            f"{cookie['name']}={cookie['value']}"
            for cookie in self.driver.get_cookies()
        ])
        r = http.request(
            url=self.driver.current_url,
            method="GET",
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Cookie": cookies_str,
            },
            redirect=False,
            retries=urllib3.Retry(
                redirect=0,
                raise_on_redirect=False,
            ),
        )
        return r.status

    def wait_for_animation(self) -> None:
        wait_for_animation(self.driver)

    def wait_document_status(self, seconds: float = NORMAL_LOAD_TIME) -> None:
        wait_document_status(self.driver, seconds=seconds)

    def wait_websocket_connection_open(
        self, seconds: float = NORMAL_LOAD_TIME
    ) -> None:
        wait_websocket_connection_open(self.driver, seconds=seconds)

    def wait_for_alert(self, seconds: float = NORMAL_LOAD_TIME) -> Alert:
        return wait_for_alert(self.driver, seconds=seconds)

    def is_alert_displayed(self, seconds: float = NORMAL_LOAD_TIME) -> bool:
        return wait_for_alert_is_displayed(self.driver, seconds=seconds)

    def switch_to_tab(self) -> None:
        new_window = wait_until_new_window_is_opened(
            self.driver, self.previous_window_handle
        )
        switch_to_window(self.driver, new_window)

    def switch_previous_tab(self) -> None:
        switch_to_window(self.driver, self.previous_window_handle)

    def scroll_to_bottom(self) -> None:
        scroll_to_bottom(self.driver)

    def scroll_to_top(self) -> None:
        scroll_to_top(self.driver)

    def scroll_into_end(self) -> None:
        scroll_into_end(self.driver)

    def find_network_log(
        self, find_mask: str, find_status: int = 200, timeout: float = 5
    ) -> list:
        return find_network_log(self.driver, find_mask, find_status, timeout)

    def set_local_storage(self, key: str, value: str) -> None:
        set_local_storage(self.driver, key, value)


class Bindable:
    def bind(self, parent: Any, driver: Any, parent_cls: Any = None) -> Any:
        c = self.__class__.__new__(self.__class__)
        c.__dict__ = self.__dict__.copy()
        c.parent = parent
        c.parent_cls = parent_cls
        c.driver = driver
        return c

    def __get__(self, instance: Any, owner: Any) -> Any:
        return self.bind(instance.lookup(), instance.driver, instance)


class Base(Bindable):
    def __init__(self, by: str, locator: str) -> None:
        self.by = by
        self.locator = locator

    index = 0
    parent = None
    driver = None
    parent_cls = None
    _cached_elements = None

    @property
    def is_mobile(self) -> bool:
        """Return True if test run like mobile device"""
        return (
            "mobile"
            in self.driver.execute_script("return navigator.userAgent;").lower()
        )

    @property
    def is_desktop(self) -> bool:
        """Return True if test run like desktop device"""
        return not self.is_mobile

    def _refresh_parent(self) -> None:
        if self.parent_cls:
            self.driver = self.parent_cls.driver
            self.parent = self.parent_cls.lookup()

    def _get_current_driver(self) -> WebDriver | WebElement:
        """
        Returned WebDriver or WebElement
        :return: obj
        """
        return self.parent if self.parent is not None else self.driver

    def _validate_locator(self) -> tuple[str, str]:
        """
        Validate XPATH locators:
        locator mast have start "."
        for example ".//*[@id='cabinet']"
        :return tuple[str, str]
        """
        if isinstance(self._get_current_driver(), WebElement):
            if self.by == By.XPATH and not self.locator.startswith("."):
                raise LocatorException(
                    f'Xpath locator must start with "." (dot). '
                    f'Please check this locator "{self.locator}"'
                )
        return self.by, self.locator

    def _find_elements(self) -> list[WebElement]:
        driver = self._get_current_driver()
        locator = self._validate_locator()
        try:
            self._cached_elements = driver.find_elements(*locator)
        except StaleElementReferenceException:
            self._refresh_parent()
            driver = self._get_current_driver()
            self._cached_elements = driver.find_elements(*locator)
        return self._cached_elements

    @with_retries(MAX_TRIES, 0.5)
    def _finder(self, force: bool = False) -> list[WebElement]:
        """
        Used cache, find element only first call
        :return: self._cached_elements
        """
        if force or not self._cached_elements:
            self._find_elements()
        return self._cached_elements


class Collection(Base, Sequence):
    def __iter__(self) -> Iterator:
        for i in range(len(self)):
            yield self[i]

    def get_item(self, index: int) -> Any:
        item_name = f"{self.base.__name__}Item"
        params = {
            "parent": self.parent,
            "driver": self.driver,
            "parent_cls": self.base.parent_cls,
            "_cached_elements": self._cached_elements,
            "index": index,
        }
        return type(item_name, (self.base,), params)(self.by, self.locator)

    def __getitem__(self, val: Any) -> Any | list[Any]:
        if isinstance(val, slice):
            start, stop, step = val.indices(len(self))
            return [self.get_item(i) for i in range(start, stop, step)]

        return self.get_item(val)

    def __len__(self) -> int:
        return len(self._find_elements())

    def is_empty(self) -> bool:
        return len(self) < 1

    def is_not_empty(self) -> bool:
        return not self.is_empty()

    def random_choice(self) -> Any:
        elements = self.wait_not_empty()
        index = random.randint(0, len(elements) - 1)
        return self.get_item(index)

    def wait_empty(self, timeout: float = 10) -> Self:
        msg = (
            f"Collection with {self.by}={self.locator} "
            f"is not empty after {timeout}"
        )
        wait_until(self.driver, lambda e: self.is_empty(), timeout, msg)
        return self

    def wait_not_empty(self, timeout: float = 10) -> Self:
        msg = (
            f"Collection with {self.by}={self.locator} is empty after {timeout}"
        )
        wait_until(self.driver, lambda e: self.is_not_empty(), timeout, msg)
        return self

    def filter_by(self, child_locator: str) -> Self:
        """
        Filtered blocks contained child CSS locator for example:
        Get product_blocks have buy_button
        :param str child_locator: example [data-qaid="buy_button"]
        """
        script = f"return $('{self.locator}:has({child_locator})');"
        results = self.driver.execute_script(script)
        if not results:
            raise ElementLocationException(
                f"Not found elements with {child_locator}"
            )
        self._cached_elements = results
        return self

    def find_all(self, by: str, locator: str) -> Any:
        """
        Changed locator for lookup
        :param str by: example By.CSS_SELECTOR
        :param str locator: example [data-qaid="some-locator"]
        :return: Collection
        """
        c = self.bind(self.parent, self.driver, self)
        c.by = by
        c.locator = locator
        return c

    def find(self, by: str, locator: str) -> Any:
        """
        Changed locator for lookup
        :param str by: example By.CSS_SELECTOR
        :param str locator: example [data-qaid="some-locator"]
        :return: Element
        """
        return self.find_all(by, locator).get_item(0)

    def find_by_text(
        self, text: str, check_negative: bool = False, partial_text: bool = True
    ) -> "Element":
        if partial_text:
            script = """
                var el = arguments[0];
                var text = arguments[1];
                var element
                var index;
                if (el.innerText.includes(text)) element = true;
                return element
                """
        else:
            script = """
                var el = arguments[0];
                var text = arguments[1];
                var element
                var index;
                if (el.innerText == text) element = true;
                return element
            """
        found_elements_by_test = [
            element
            for element in self
            if self.driver.execute_script(script, element.lookup(), text)
        ]
        if len(found_elements_by_test) == 0:
            if check_negative:
                return False
            raise PromiumException(
                f'Element with text "{text}" has not been found'
            )
        return found_elements_by_test[0]

    @property
    def first_item(self) -> Any:
        return self.wait_not_empty().get_item(0)

    @property
    def last_item(self) -> Any:
        return self.wait_not_empty().get_item(-1)


@add_logger_to_base_element_classes
class ElementBase(Base):
    def _get_element(self) -> WebElement:
        if self.index >= len(self._cached_elements):
            raise PromiumException(
                f"Collection by={self.by} locator={self.locator} "
                f"has been changed, get {self.index} of "
                f"{len(self._cached_elements) - 1} elements"
            )
        return self._cached_elements[self.index]

    @highlight_element
    def lookup(self) -> WebElement:
        try:
            self._cached_elements = self._finder()
            element = self._get_element()
            element.is_displayed()
        except StaleElementReferenceException:
            self._refresh_parent()
            self._cached_elements = self._finder(force=True)
            element = self._get_element()
        return element

    @classmethod
    def as_list(cls, by: str, locator: str) -> Any:
        params = {"parent": cls.parent, "driver": cls.driver, "base": cls}
        return type(f"{cls.__name__}List", (Collection,), params)(by, locator)

    def wait_to_display(self, timeout: int = 10, msg: str = "") -> Self:
        """
        Waited to display element in the visible area of the page.
        :param int timeout:
        :param str msg:
        :return: Element
        """
        obj = self._get_current_driver()
        try:
            WebDriverWait(
                obj,
                timeout,
                ignored_exceptions=[
                    WebDriverException,
                    ElementLocationException,
                ],
            ).until(lambda driver: self.is_displayed())
            return self
        except TimeoutException as e:
            if self.is_present():
                msg = (
                    f"Element with {self.by}={self.locator} was found "
                    f"but was not displayed after {timeout} seconds"
                    f"\n{msg}"
                )
            else:
                msg = (
                    f"Element with {self.by}={self.locator} not found "
                    f"after {timeout} seconds"
                    f"\n{msg}"
                )
            raise ElementLocationException(msg) from e

    def wait_to_present(self, timeout: int = 10, msg: str = "") -> Self:
        """
        Waited to present element in DOM.
        :param int timeout:
        :param str msg:
        :return: Element
        """
        wait_until(
            self.driver,
            is_present(self),
            timeout,
            f"Element with {self.by}={self.locator} not found "
            f"after {timeout} seconds"
            f"\n{msg}",
        )
        return self

    def wait_to_disappear(self, time: int = 10, msg: str = "") -> bool | None:
        def _find_no_visible_element(self: Self) -> bool | None:
            obj = self._get_current_driver()
            try:
                return not obj.find_element(self.by, self.locator).is_displayed()
            except (
                NoSuchElementException,
                StaleElementReferenceException,
                WebDriverException,
            ):
                return True

        return WebDriverWait(self.driver, time).until(
            lambda driver: _find_no_visible_element(self),
            msg
            if msg
            else f"Element with {self.by}={self.locator} did not disappear "
            f"after {time} seconds",
        )

    def wait_in_viewport(self, time: int = 5) -> Self:
        jquery_script = """
            var elem = arguments[0],
            box = elem.getBoundingClientRect(),
            cx = box.left + box.width / 2,
            cy = box.top + box.height / 2,
            e = document.elementFromPoint(cx, cy);
            for (; e; e = e.parentElement) {
                if (e === elem)
                    return true;
            }
            return false;
            """

        wait_until(
            driver=self.driver,
            expression=lambda driver: driver.execute_script(
                jquery_script, self.lookup()
            ),
            seconds=time,
            msg=f"Element with {self.by}={self.locator} did not appear "
            f"in viewport after {time} seconds",
        )
        return self

    def wait_part_appear_in_class(
        self, part_class: str, msg: str = None
    ) -> None:
        wait_part_appear_in_class(
            driver=self.driver,
            obj=self.lookup(),
            part_class=part_class,
            msg=msg,
        )

    def wait_part_disappear_in_class(
        self, part_class: str, msg: str = None
    ) -> None:
        wait_part_disappear_in_class(
            driver=self.driver,
            obj=self.lookup(),
            part_class=part_class,
            msg=msg,
        )

    def scroll(self, base_element: Any = None) -> None:
        scroll_to_element(self.driver, self.lookup(), base_element)

    def get_attribute(self, name: str) -> str | None:
        return self.lookup().get_attribute(name)

    def check_class_part_presence(self, class_name: str) -> str | None:
        return class_name in self.lookup().get_attribute("class")

    @property
    def location(self) -> dict:
        return self.lookup().location

    def is_present(self) -> bool:
        """Checks if element is present on page at current time"""
        try:
            return bool(self._find_elements())
        except WebDriverException as e:
            log.error(f"[PROMIUM] Original webdriver exception: {e}")
            return False

    @property
    def text(self) -> str:
        return self.lookup().text

    def click(self) -> None:
        """custom click, with blackjack and hookers"""
        self.scroll_into_view()
        self.lookup().click()

    def js_click(self) -> None:
        self.driver.execute_script("arguments[0].click()", self.lookup())

    def is_displayed(self) -> bool:
        if not self.is_present():
            return False
        return self.lookup().is_displayed()

    def hover_over(self) -> None:
        ActionChains(self.driver).move_to_element(self.lookup()).perform()

    def hover_over_with_offset(self, xoffset: int = 1, yoffset: int = 1) -> None:
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def click_with_offset(self, xoffset: int = 1, yoffset: int = 1) -> None:
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).click().perform()

    def move_to_element_and_click(self) -> None:
        ActionChains(self.driver).move_to_element(
            self.lookup()
        ).click().perform()

    @property
    def element_title(self) -> str | None:
        return self.get_attribute("title")

    @property
    def element_id(self) -> str | None:
        return self.get_attribute("id")

    def value_of_css_property(self, property_name: str) -> str:
        """Returns the value of a CSS property"""
        return self.lookup().value_of_css_property(property_name)

    def scroll_into_view(
        self,
        behavior: str = "instant",
        block: str = "center",
        inline: str = "center",
    ) -> Self:
        """
        Method scrolls the element on which it's called into the visible
        area of the browser window.

        element.scrollIntoView();
        element.scrollIntoView(scrollIntoViewOptions); // Object parameter

        :Args:
        - behavior - Defines the transition animation. One of "auto" or
            "smooth" or "instant".
        - block - Defines vertical alignment. One of "start", "center",
            "end", or "nearest".
        - inline - Defines horizontal alignment. One of "start", "center",
            "end", or "nearest".
        """
        options = {"behavior": behavior, "block": block, "inline": inline}
        self.driver.execute_script(
            "arguments[0].scrollIntoView(arguments[1]);", self.lookup(), options
        )
        return self

    def drag_and_drop(self, target: Any) -> None:
        ActionChains(self.driver).drag_and_drop(
            self.lookup(), target.lookup()
        ).perform()


class Block(ElementBase):
    pass


class Element(ElementBase):
    @property
    def tag_name(self) -> str:
        """Gets this element's tagName property."""
        return self.lookup().tag_name

    def submit(self) -> None:
        """Submits a form."""
        return self.lookup().submit()

    def is_selected(self) -> bool:
        """
        Can be used to check if a checkbox or radio button is selected.
        """
        return self.lookup().is_selected()

    def is_enabled(self) -> bool:
        """Whether the element is enabled."""
        return self.lookup().is_enabled()

    @property
    def location_once_scrolled_into_view(self) -> dict:
        """CONSIDERED LIABLE TO CHANGE WITHOUT WARNING.
        Use this to discover where on the screen an element is
        so that we can click it. This method should cause
        the element to be scrolled into view.

        Returns the top lefthand corner location on the screen,
        or None if the element is not visible
        """
        return self.lookup().location_once_scrolled_into_view

    @property
    def size(self) -> dict:
        """Returns the size of the element"""
        return self.lookup().size

    @property
    def id(self) -> str:  # noqa A003
        """Returns internal id used by selenium.

        This is mainly for internal use.  Simple use cases such as checking
        if 2 webelements refer to the same element, can be done using '=='::

            if element1 == element2:
                print("These 2 are equal")

        """
        return self.lookup().id

    def wait_to_staleness(self) -> Self:
        return wait_until(
            driver=self.driver,
            expression=EC.staleness_of(self.lookup()),
            seconds=10,
        )

    def wait_frame_and_switch_to_it(self) -> Self:
        return wait_until(
            driver=self.driver,
            expression=(
                EC.frame_to_be_available_and_switch_to_it(self.lookup())
            ),
            seconds=10,
        )

    def wait_for_text_present(self, text: str) -> Self:
        return wait_until(
            driver=self.driver,
            seconds=10,
            expression=text_to_be_present_in_element(self, text),
            msg=f"Text: {text}, does not appear after 10 seconds",
        )

    def set_inner_html(self, value: str) -> None:
        self.driver.execute_script(
            f'arguments[0].innerHTML = "{value}"', self.lookup()
        )

    def hover_over_and_click(self, on_element: Any = None) -> None:
        ActionChains(self.driver).move_to_element(self.lookup()).click(
            on_element.lookup()
        ).perform()

    def drag_and_drop_by_offset(self, xoffset: int, yoffset: int) -> None:
        ActionChains(self.driver).drag_and_drop_by_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def wait_for_changes_text_attribute(self, name_attr: str, text: str) -> Self:
        return wait_until(
            driver=self.driver,
            expression=lambda driver: text != self.get_attribute(name_attr),
            seconds=10,
            msg="Text attribute has not changed",
        )

    def wait_for_text_change(self, text: str = None) -> Self:
        element_text = text if type(text) is str else self.text
        return wait_until(
            driver=self.driver,
            expression=lambda driver: element_text != self.text,
            seconds=5,
            msg=f'Text "{element_text}" not changed',
        )

    def wait_to_enabled(self, time: int = 10) -> Self:
        try:
            wait = WebDriverWait(
                self.driver, time, ignored_exceptions=[WebDriverException]
            )
            message = (
                f"Element with {self.by}={self.locator} "
                f"not enabled after {time} seconds"
            )
            return wait.until(
                lambda driver: False
                if self.get_attribute("disabled") == "true"
                else self,
                message,
            )
        except TimeoutException as e:
            raise ElementLocationException(e.msg) from e
