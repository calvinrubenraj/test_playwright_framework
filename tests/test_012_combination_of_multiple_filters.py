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
@allure.feature("Combination of Multiple Filters")
def test_012_combination_of_multiple_filters(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    test_value = test_data["test_001_verify_popular_page"]

    year_range = test_data["test_009_filter_by_valid_year_range"]
    rating_range = test_data["test_010_filter_by_rating"]
    genre_id = test_data["test_011_filter_by_genre"]["genre"]["comedy"]


    with allure.step("Open application "):
        #goto landing page(popular)
        page.goto("/")
        page.wait_for_load_state("networkidle")

    with allure.step("Select Top rate and given filter and validate the response status, request payload"):
        #Select api contains movie

        popularpage.top_rated_tab_button_locator.click()
        page.wait_for_timeout(100)
        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        popularpage.select_min_year(year_range["min_year"])
        page.wait_for_timeout(100)
        popularpage.select_max_year(year_range["max_year"])

        box = popularpage.rating_position_locator.bounding_box()
        if box:
            right_x = box["width"] - 7
            center_y = box["height"] / 2
            popularpage.rating_position_locator.click(position={"x": right_x, "y": center_y})
        page.wait_for_timeout(500)

        with page.expect_response(
                lambda response:
                "discover/movie" in response.url.lower()
        ) as response_info:
            popularpage.select_genre("Comedy")
        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page with Top rate category and all filter",
            attachment_type=allure.attachment_type.PNG
        )

        response = response_info.value
        reqest_payload = response.url
        payload = reqest_payload.split("?")[1]
        payload_dict = { payload_raw.split("=")[0]: payload_raw.split("=")[1] for payload_raw in payload.split("&") }

        # Validate payload has the correct year range
        assert year_range["min_year"] == payload_dict["release_date.gte"].split('-')[0]
        assert year_range["max_year"] == payload_dict["release_date.lte"].split('-')[0]

        # Validate payload has the correct year range
        assert rating_range["min_rating"] == payload_dict["vote_average.gte"]
        assert rating_range["max_rating"] == payload_dict["vote_average.lte"]

        #Validate payload has the correct year range
        assert genre_id == int(payload_dict["with_genres"])

    with allure.step("Validate the the response order in vote_avaerage is descending"):
        with subtests.test(msg="Validate the the response order in vote_avaerage is descending"):
            # Validation of the response data is a descending order related to popularity
            response_body = response.json()
            MovieAPIValidator.validate_vote_average_descending(response_body)

    with allure.step("Validate the api result is filter to the given year range"):
        with subtests.test(msg="Validate the api result is filter to the given year range"):
            response_body = response.json()
            MovieAPIValidator.validate_year_range(response_body, year_range["min_year"], year_range["max_year"])

    with allure.step("Validate the api result is filter to the given  rating vote_average range"):
        with subtests.test(msg="Validate the api result is filter to the given year range"):
            response_body = response.json()
            MovieAPIValidator.validate_rating_range(response_body, rating_range["min_rating"], rating_range["max_rating"])

    with allure.step("Validate the api result filter only the genre id is contains"):
        with subtests.test(msg="Validate the api result filter only the genre id is contains"):
            response_body = response.json()
            MovieAPIValidator.validate_genre_id(response_body, genre_id)

    with allure.step("Validate the movie cards is same as api response of combined filter and top rated order"):
        with subtests.test(msg="Validate the movie cards is same as api response of combined filter and top rated order"):
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