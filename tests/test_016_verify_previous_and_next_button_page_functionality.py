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
@allure.feature("Verify Previous and Next button page Functionality")
def test_016_verify_previous_and_next_button_page_functionality(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    previous_loaded_page_movies_title_list = []
    default_page_no = 1

    with allure.step("Open application with default url"):
        page.goto("/")
        page.wait_for_load_state("networkidle")
        #get the response data
        with page.expect_response(
                lambda response:
                "movie/now_playing" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.newest_tab_button_locator.click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page 1",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step(f"Validate the page {default_page_no} is default, response status code, payload contains 'page={default_page_no}' and response has page={default_page_no}"):
        page_no=str(default_page_no)
        #Validation of the response status code
        MovieAPIValidator.validate_status(response)

        #Validate the Url payload has page=1
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        #Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"

    with allure.step("Validate the previous button is disabled and next button is enabled due selected is first page"):
        expect(popularpage.get_previous_button_locator()).to_have_attribute("aria-disabled", "true"), "Previous button is enabled"
        expect(popularpage.get_next_button_locator()).to_have_attribute("aria-disabled", "false"), "Next button is enabled"

    with allure.step("Click on the next button and validate the page 2 is selected in UI"):
        page_no="2"
        with page.expect_response(
                lambda response:
                "movie/now_playing" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_next_button_locator().click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        # Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"
        with allure.step(f"Validate the page {page_no} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Goto last page and validate the previous button is enabled and next button is disabled"):
        last_page_no_ui_loc = popularpage.get_last_page_number_locator()
        last_page_no_ui_loc.click()
        last_page_no_ui = popularpage.get_last_page_number()

        with allure.step(
                "Validate the previous button is enabled and next button is disabled due selected is first page"):
            expect(popularpage.get_previous_button_locator()).to_have_attribute("aria-disabled", "false"), "Previous button is enabled"
            expect(popularpage.get_next_button_locator()).to_have_attribute("aria-disabled", "true"), "Next button is enabled"

    with allure.step("Click on the next button and validate the page { is selected in UI"):
        page_no=str(int(last_page_no_ui)-1)
        with page.expect_response(
                lambda response:
                "movie/now_playing" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_previous_button_locator().click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        # Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"
        with allure.step(f"Validate the page {page_no} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )

