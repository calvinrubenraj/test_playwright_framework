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
@pytest.mark.known_issue
@allure.epic("UI")
@allure.feature("Direct Navigation to All Category")
def test_017_directly_navigation_to_all_category(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    #import test data
    test_value = test_data["test_001_verify_popular_page"]


    with allure.step("Open application with default url"):

        #get the response data
        with page.expect_response(
                lambda response:
                "/3/movie/popular" in response.url
                and response.request.method == "GET"
        ) as response_info:
            page.goto("/")
            page.wait_for_load_state("networkidle")

        response = response_info.value

        #Validation of the response status code
        MovieAPIValidator.validate_status(response)
        response_body = response.json()
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the popular page",
            attachment_type=allure.attachment_type.PNG
        )

    with (allure.step("Verify Direct navigation to Popular page")):
       with subtests.test(msg="Verify Direct navigation to popular page"):
           response = page.goto("/popular")
           # Assert that the response status is 404
           assert response.status == 200, f"Expected page load success, but got {response.status}"

    with (allure.step("Verify Direct navigation to Trending page")):
       with subtests.test(msg="Verify Direct navigation to trending page"):
           response = page.goto("/trend")
           # Assert that the response status is 404
           assert response.status == 200, f"Expected page load success, but got {response.status}"

    with (allure.step("Verify Direct navigation to Newest page")):
       with subtests.test(msg="Verify Direct navigation to newest page"):
           response = page.goto("/new")
           # Assert that the response status is 404
           assert response.status == 200, f"Expected page load success, but got {response.status}"

    with (allure.step("Verify Direct navigation to Top rated page")):
       with subtests.test(msg="Verify Direct navigation to Top rated page"):
           response = page.goto("/top")
           # Assert that the response status is 404
           assert response.status == 200, f"Expected page load success, but got {response.status}"
