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
@allure.feature("Verify First Section pagination Functionality")
def test_013_verify_first_section_pagination_funtionality(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    previous_loaded_page_movies_title_list = []


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

    with allure.step("Validate the page 1 is default, response status code, payload contains 'page=1' and response has page=1"):
        page_no="1"
        #Validation of the response status code
        MovieAPIValidator.validate_status(response)

        #Validate the Url payload has page=1
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        #Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"

    with allure.step("Validate the page 1 is select in UI and get the list of movie title"):
        #Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == page_no, f"The selected page number is not match with api page number"

        #store the page 1 movie list in loaded_page_movies_title_list
        previous_loaded_page_movies_title_list= [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]

    with allure.step("Click on the page 2 and validated the page 2 is selected in UI"):
        page_no="2"
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_page_locator_with_page_no(page_no).click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page 2",
            attachment_type=allure.attachment_type.PNG
        )
        # Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == page_no, f"The selected page number is not match with api page number"

    with allure.step("Validate the page 2 response status code, payload contains 'page=2' and response has page=2"):
        #Validation of the response status code
        MovieAPIValidator.validate_status(response)

        #Validate the Url payload has page=1
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        #Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"

        with allure.step("Get the Movie title list and validate page 2 movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_2_movies_title_list = [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_2_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page 2 and previous page movies titles list:{common_movie_title}"
            previous_loaded_page_movies_title_list.extend(page_2_movies_title_list)

    with allure.step("Click on the page 3 and validated the page 3 is selected in UI"):
        page_no="3"
        with page.expect_response(
                lambda response:
                "/3/movie/" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_page_locator_with_page_no(page_no).click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page 3",
            attachment_type=allure.attachment_type.PNG
        )
        # Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == page_no, f"The selected page number is not match with api page number"

        with allure.step("Get the Movie title list and validate page 3 movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_3_movies_title_list = [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_3_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page 3 and previous page movies titles list:{common_movie_title}"
            previous_loaded_page_movies_title_list.extend(page_3_movies_title_list)

    with (allure.step("Validate the page 4 is available in UI and able to click on the page 4")):
        page_no="4"
        page_4_locator = popularpage.page_section_locator.get_by_role("button", name=f"Page {page_no}")
        expect(page_4_locator).to_be_visible(timeout=10000)
        page_4_locator.click()
        page.wait_for_timeout(1000)
        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the page 4",
            attachment_type=allure.attachment_type.PNG
        )

        with allure.step(
                "Get the Movie title list and validate page 4 movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_4_movies_title_list = [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_4_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page 4 and previous page movies titles list:{common_movie_title}"



