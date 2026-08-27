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
@allure.feature("Search/Filter using valid title validation")
def test_005_search_filter_using_valid_title(page: Page, settings):
    #page initialization
    popularpage = CategoryPage(page)

    #import test data
    test_value = test_data["test_005_search_filter_using_valid_title"]


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
                name="Screenshot of the Search movie",
                attachment_type=allure.attachment_type.PNG
            )
            #get the movie details list
            movie_details = popularpage.get_movie_cards()
            assert len(movie_details) > 0, "There is no movie card in the popular page"

            #validate each title of the movies should contain the search text
            list_of_movies_title = [card["title"] for card in movie_details]
            movies_without_search_text = []

            for movie_title in list_of_movies_title:
                if search(search_data, movie_title, flags=re.IGNORECASE):
                    continue
                else:
                    movies_without_search_text.append(movie_title)
            allure.attach(f"The movies title after searching text = '{search_data}': " + str(list_of_movies_title),
                          name="Details of the loaded movies after searching",
                          attachment_type=allure.attachment_type.TEXT)

            assert len(movies_without_search_text) == 0, f"The movie title {movies_without_search_text} does not contain the search text {search_data}"