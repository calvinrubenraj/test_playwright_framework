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
@allure.feature("Verify Middle Section pagination Functionality")
def test_015_verify_middle_section_pagination_funtionality(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    previous_loaded_page_movies_title_list = []
    default_page_no = 1

    with allure.step("Open application with default url"):

        #get the response data
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            page.goto("/")
            page.wait_for_load_state("networkidle")
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

    with allure.step(f"Click the '...' in page section and validate the page jump to {default_page_no+3}"):
        page_no=str(default_page_no+3)
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_break_page_button_locator().click()
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
        with allure.step(f"Validate the page {default_page_no+3} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step(f"Click the '...' again in page section and validate the page jump to {default_page_no+3+3}"):
        page_no=str(default_page_no+3+3)
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_break_page_button_locator().click()
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
        with allure.step(f"Validate the page {default_page_no+3+3} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step(f"Validate the two break button is visible in page section"):
        assert popularpage.get_break_page_button_locator().count() == 2, f"Two break button is not visible in page section"

    with allure.step(f"Click the second break button'...' in page section and validate the page jump to {default_page_no+3+3+3}"):
        page_no=str(default_page_no+3+3+3)
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_break_page_button_locator().nth(1).click()
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
        with allure.step(f"Validate the page {default_page_no+3+3+3} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"

        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step(
            f"Click the first break button'...' in page section and validate the page jump to {default_page_no + 3 + 3}"):
        page_no = str(default_page_no + 3 + 3)
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_break_page_button_locator().nth(0).click()
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
        with allure.step(f"Validate the page {default_page_no + 3 + 3} is selected in UI"):
            selected_page_no = popularpage.get_selected_page_number()
            assert selected_page_no == page_no, f"The selected page number is not match with api page number"

        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {page_no}",
            attachment_type=allure.attachment_type.PNG
        )
