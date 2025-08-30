import pytest
from bs4 import BeautifulSoup

from promium.test_case import RequestTestCase


@pytest.mark.request
class TestMainPage(RequestTestCase):
    test_case_url = "some url with test case"

    def test_google_search_block(self):
        page_text = self.get_response("https://prom.ua/ua/").data
        soup = BeautifulSoup(page_text, "html.parser")

        search_input = soup.find(attrs={"name": "search_term"})
        self.soft_assert_true(search_input, "Не найдена строка поиска")

        search_btn = soup.find(attrs={"data-qaid": "search_btn"})
        self.soft_assert_equals(
            search_btn.text, "Знайти", "Не правильное название кнопки поиска"
        )
