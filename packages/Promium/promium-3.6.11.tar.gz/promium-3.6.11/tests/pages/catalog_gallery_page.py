from selenium.webdriver.common.by import By

from promium import Block, Page

from tests.urls import collect_url


class ProductTilBlock(Block):
    pass


class ProductsBlock(Block):
    product_blocks = ProductTilBlock.as_list(
        By.CSS_SELECTOR, '[data-qaid="product_block"]'
    )


class CatalogGalleryPage(Page):
    url = collect_url("{query}")

    gallery_block = ProductsBlock(
        By.CSS_SELECTOR, '[data-qaid="product_gallery"]'
    )
