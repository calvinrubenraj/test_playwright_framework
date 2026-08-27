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
@allure.feature("Trend Page validation")
def test_002_verify_trending_category(page: Page, settings):
    #page initialization
    trendingpage = CategoryPage(page)

    #import test data
    test_value = test_data["test_001_verify_popular_page"]


    with allure.step("Open application, validate url, trend api and screenshot of page"):

        with allure.step("Validate trend api response status, schema"):
            #land in home page
            page.goto("/")
            page.wait_for_load_state("networkidle")
            #get the response data
            with page.expect_response(
                    lambda response:
                    "3/trending/movie/week" in response.url
                    and response.request.method == "GET"
            ) as response_info:
                trendingpage.trend_tab_button_locator.click()
                page.wait_for_timeout(2000)
                trendingpage.loading_icon_locator = page.get_by_label("audio-loading")
                expect(trendingpage.loading_icon_locator).to_be_hidden(timeout=10000)
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



            allure.attach(f"The response status code: {response.status}\n"
                          f"The response body follows the schema\n",name="Details of the trend api response status and response validation", attachment_type=allure.attachment_type.TEXT)

        expect(page).to_have_url("https://tmdb-discover.surge.sh/trend")
        page.wait_for_timeout(3000)
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the trending page",
            attachment_type=allure.attachment_type.PNG
        )

    with (allure.step("Verify Trend page UI component")):
        with allure.step("Validation of category tab"):
            expect(trendingpage.category_element_locator).to_have_count(4)
            category_item = [ trendingpage.category_element_locator.nth(item).inner_text().strip() for item in range(trendingpage.category_element_locator.count())]
            #compare the UI category list with the reference list
            expect(trendingpage.category_element_locator).to_have_text(test_value["reference_category_tab_list"])
            #Validate selected tab is trend tab
            selected_category_tab_locator = trendingpage.category_element_locator.filter(has_text="Trend")
            expect(selected_category_tab_locator).to_have_css("color", "rgb(255, 255, 255)")
            allure.attach(
                f"the category name {str(category_item)}\n"
                f"The count of the category: {str(trendingpage.category_element_locator.count())}\n"
                f"The selected tab: {str(selected_category_tab_locator.inner_text())}\n",
                name="Details of the category tab",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validation of Movie list and Movie details"):
            card_details = trendingpage.get_movie_cards()

            assert len(card_details) > 0, "There is no movie card in the trend page"
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

        with allure.step("Validation the Movie card order does not change after changing the category and come back to trend page"):
            #goto popular page
            trendingpage.popular_tab_button_locator.click()
            page.wait_for_timeout(2000)
            trendingpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(trendingpage.loading_icon_locator).to_be_hidden(timeout=10000)

            #retrun to trend page
            trendingpage.trend_tab_button_locator.click()
            page.wait_for_timeout(2000)
            trendingpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(trendingpage.loading_icon_locator).to_be_hidden(timeout=10000)

            refreshed_card_details = trendingpage.get_movie_cards()
            assert refreshed_card_details == card_details, "The movie card order does not match the api response"
