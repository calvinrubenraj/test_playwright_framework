import re
from re import search

import pytest
import allure
from playwright.sync_api import Page, expect
from pages.category_page import CategoryPage
from test_data import test_data
from utils.api_validator import MovieAPIValidator

@pytest.mark.ui
@pytest.mark.smoke
@allure.epic("UI")
@allure.feature("Search/Filter using invalid title validation")
def test_006_search_filter_using_invalid_title(page: Page, settings):
    #page initialization
    popularpage = CategoryPage(page)

    #import test data
    test_value = test_data["test_006_search_filter_using_invalid_title"]


    with allure.step("Open application, validate url, popular api and screenshot of page"):
        page.goto("/")
        page.wait_for_load_state("networkidle")

    with allure.step("Validation of Search box functionality"):
        with allure.step("Validation of Search box element"):
            expect(popularpage.search_box_locator).to_be_visible()

        with allure.step("Validation of Search movie"):
            search_data = test_value["search_text"]
            popularpage.search_text(search_data)
            allure.attach(
                page.screenshot(type="png"),
                name="Screenshot of the Empty page",
                attachment_type=allure.attachment_type.PNG
            )

            #validate each title of the movies should contain the search text
            empty_card_locator = page.get_by_text("No results found.")

            expect(empty_card_locator).to_be_visible()