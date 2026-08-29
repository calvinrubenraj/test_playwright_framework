import re
from re import search

import pytest
import allure
import traceback
from playwright.sync_api import Page, expect
from pages.category_page import CategoryPage
from test_data import test_data
from utils.api_validator import MovieAPIValidator

@pytest.mark.ui
@pytest.mark.smoke
@allure.epic("UI")
@allure.feature("Filter by Valid Year range")
def test_009_filter_by_valid_year_range(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    year_range = test_data["test_009_filter_by_valid_year_range"]


    with allure.step("Open application "):
        #goto landing page(popular)
        page.goto("/")
        page.wait_for_load_state("networkidle")

    with allure.step("select minimum and maximum year filter and validate the response status, request payload match give year range"):
        #Select api contains movie
        popularpage.select_min_year(year_range["min_year"])
        page.wait_for_timeout(500)

        with page.expect_response(
                lambda response:
                "movie" in response.url.lower()
        ) as response_info:
            popularpage.select_max_year(year_range["max_year"])


        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page with year range filter",
            attachment_type=allure.attachment_type.PNG
        )

        response = response_info.value
        reqest_payload = response.url
        payload = reqest_payload.split("?")[1]
        payload_dict = { payload_raw.split("=")[0]: payload_raw.split("=")[1] for payload_raw in payload.split("&") }
        #Validate payload has the correct year range
        assert year_range["min_year"] == payload_dict["release_date.gte"].split('-')[0]
        assert year_range["max_year"] == payload_dict["release_date.lte"].split('-')[0]

    with allure.step("Validate the api result is filter to the given year range"):
        with subtests.test(msg="Validate the api result is filter to the given year range"):
            response_body = response.json()
            MovieAPIValidator.validate_year_range(response_body, year_range["min_year"], year_range["max_year"])

    with allure.step("Validate the movie card year is between the given year range"):
        with subtests.test(msg="Validate the movie card year is between the given year range"):
            card_details = popularpage.get_movie_cards()
            for card in card_details:
                try:
                    assert int(year_range["min_year"]) <= int(card["year"]) <= int(year_range["max_year"]), f"The movie card year is not in the given year range{card}"

                except AssertionError as error:
                    # 1. Capture the full Python error stack trace
                    error_traceback = traceback.format_exc()

                    # 2. Attach the error log as plain text to the current Allure subtest
                    allure.attach(
                        body=error_traceback,
                        name="Assertion Failure Details",
                        attachment_type=allure.attachment_type.TEXT
                    )

                    # 3. Crucial: Re-raise the error so Allure marks this subtest as Failed
                    raise error