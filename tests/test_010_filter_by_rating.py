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
@allure.feature("Filter by rating")
def test_010_filter_by_rating(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    rating_range = test_data["test_010_filter_by_rating"]


    with allure.step("Open application "):
        #goto landing page(popular)
        page.goto("/")
        page.wait_for_load_state("networkidle")

    with allure.step("click rating in four star and validate the response status, request payload match give year range"):
        #Select api contains movie

        with page.expect_response(
                lambda response:
                "movie" in response.url.lower()
        ) as response_info:
            box = popularpage.rating_position_locator.bounding_box()
            if box:
                right_x = box["width"] - 7
                center_y = box["height"] / 2
                popularpage.rating_position_locator.click(position={"x": right_x, "y": center_y})

        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page with rating filter",
            attachment_type=allure.attachment_type.PNG
        )

        response = response_info.value
        reqest_payload = response.url
        payload = reqest_payload.split("?")[1]
        payload_dict = { payload_raw.split("=")[0]: payload_raw.split("=")[1] for payload_raw in payload.split("&") }
        #Validate payload has the correct year range
        assert rating_range["min_rating"] == payload_dict["vote_average.gte"]
        assert rating_range["max_rating"] == payload_dict["vote_average.lte"]

    with allure.step("Validate the api result is filter to the given  rating vote_average range"):
        with subtests.test(msg="Validate the api result is filter to the given year range"):
            response_body = response.json()
            MovieAPIValidator.validate_rating_range(response_body, rating_range["min_rating"], rating_range["max_rating"])

    with allure.step("Validate the movie cards is same as api response of rating filter"):
        with subtests.test(msg="Validate the movie cards is same as api response of rating filter"):
            card_details = popularpage.get_movie_cards()
            card_list_title = [ card["title"] for card in card_details ]
            api_movie_title = [movie["title"] for movie in response_body["results"]]
            try:
                assert card_list_title == api_movie_title, f"The movie card list is not match the api movie card list"

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