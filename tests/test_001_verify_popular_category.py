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
@allure.feature("Popular Page validation")
def test_001_verify_popular_category(page: Page, settings):
    #page initialization
    popularpage = CategoryPage(page)

    #import test data
    test_value = test_data["test_001_verify_popular_page"]


    with allure.step("Open application, validate url, popular api and screenshot of page"):

        with allure.step("Validate popular api response status, schema and data is descending order related to popularity"):
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

            # Response schema validation
            MovieAPIValidator.validate_response_structure(
                response_body
            )
            for movie in response_body["results"]:
                MovieAPIValidator.validate_movie_schema(movie)

            # Validation of the response data is a descending order related to popularity
            MovieAPIValidator.validate_popularity_descending(response_body)

            allure.attach(f"The response status code: {response.status}\n"
                          f"The response result is in descending order popularity\n"
                          f"The response body follows the schema\n",name="Details of the popular api response status and response validation", attachment_type=allure.attachment_type.TEXT)

        expect(page).to_have_url("https://tmdb-discover.surge.sh/popular")
        page.wait_for_timeout(3000)
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the popular page",
            attachment_type=allure.attachment_type.PNG
        )

    with (allure.step("Verify Popular page UI component")):
        with allure.step("Validation of category tab"):
            expect(popularpage.category_element_locator).to_have_count(4)
            category_item = [ popularpage.category_element_locator.nth(item).inner_text().strip() for item in range(popularpage.category_element_locator.count())]
            #compare the UI category list with the reference list
            expect(popularpage.category_element_locator).to_have_text(test_value["reference_category_tab_list"])
            #Validate selected tab is popular tab
            selected_category_tab_locator = popularpage.category_element_locator.filter(has_text="Popular")
            expect(selected_category_tab_locator).to_have_css("color", "rgb(255, 255, 255)")
            allure.attach(
                f"the category name {str(category_item)}\n"
                f"The count of the category: {str(popularpage.category_element_locator.count())}\n"
                f"The selected tab: {str(selected_category_tab_locator.inner_text())}\n",
                name="Details of the category tab",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validation of Movie list and Movie details"):
            card_details = popularpage.get_movie_cards()

            assert len(card_details) > 0, "There is no movie card in the popular page"
            allure.attach(
                f"The movie card details: {str(card_details)}\n"
                f"The count of the movie card details: {str(len(card_details))}",
                name="Details of the category",
                attachment_type=allure.attachment_type.TEXT
            )

            with allure.step("Validation of Movie card details"):
                for card in card_details:
                    assert card["title"] != "", "The movie card title is empty"
                    assert card["genre"] != "", "The movie card genre is empty"
                    assert card["image_url"] != "", "The movie card image url is empty"
                    assert card["year"] != "", "The movie card description is empty"

        with allure.step("Validation of UI movie card is following same order with the api movie title"):
            api_movie_title = [movie["title"] for movie in response_body["results"]]
            ui_movie_title = [card["title"] for card in card_details]
            assert api_movie_title == ui_movie_title, "The movie card order does not match the api response"
