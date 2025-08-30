import pytest

from promium.test_case import WebDriverTestCase
from promium.waits import wait_url_contains

from tests.pages.catalog_404_page import Catalog404Page
from tests.urls import collect_url


@pytest.mark.se
class Test404CatalogPage(WebDriverTestCase):
    test_case_url = "some url with test case"

    def test_catalog_404_page_check_elements(self) -> None:
        catalog_404_page = Catalog404Page(self.driver)
        catalog_404_page.open()
        catalog_404_page.wait_for_page_loaded()
        self.soft_assert_equals(
            catalog_404_page.main_404_title.text,
            "Оо! Страница не найдена",
            "Не правильно указан основной title на странице 404.",
        )
        self.soft_assert_in(
            "Похоже такой страницы больше нет",
            catalog_404_page.suggest_404_title.text,
            "Не правильно указан suggest title на странице 404.",
        )

        fake_search_query = 666
        catalog_404_page.search_input.send_keys(fake_search_query)
        catalog_404_page.search_button.click()
        wait_url_contains(
            self.driver,
            collect_url(f"search?search_term={fake_search_query}"),
        )
