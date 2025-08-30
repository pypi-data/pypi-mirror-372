import pytest

from promium.device_config import ANDROID_360_640, XIAOMI_REDMI_7
from promium.test_case import WebDriverTestCase

from tests.pages.catalog_gallery_page import CatalogGalleryPage


@pytest.mark.se
class TestCatalogGallery(WebDriverTestCase):
    test_case_url = "some url with test case"

    def test_view_products_gallery_blocks(self):
        catalog_gallery_page = CatalogGalleryPage(self.driver)
        catalog_gallery_page.open(query="Komplekty-nizhnego-belya")
        catalog_gallery_page.wait_for_page_loaded()
        products_block = catalog_gallery_page.gallery_block
        products_block.wait_to_display(timeout=20)
        products = products_block.product_blocks
        products.first_item.wait_to_display()

    @pytest.mark.device(XIAOMI_REDMI_7)
    @pytest.mark.device(ANDROID_360_640)
    @pytest.mark.parametrize(
        "device",
        [
            pytest.param("xiaomi", marks=pytest.mark.device(XIAOMI_REDMI_7)),
            pytest.param("android", marks=pytest.mark.device(ANDROID_360_640)),
        ],
    )
    def test_mobile_view_products_gallery_blocks(self, device):
        catalog_gallery_page = CatalogGalleryPage(self.driver)
        catalog_gallery_page.open(query="Komplekty-nizhnego-belya")
        catalog_gallery_page.wait_for_page_loaded()
        products_block = catalog_gallery_page.gallery_block
        products_block.wait_to_display(timeout=20)
        products_block.product_blocks.first_item.wait_to_display()
