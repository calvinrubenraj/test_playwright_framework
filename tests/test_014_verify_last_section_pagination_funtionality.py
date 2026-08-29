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
@allure.feature("Verify Last Section pagination Functionality")
def test_014_verify_last_section_pagination_funtionality(page: Page, settings, subtests):
    #page initialization
    popularpage = CategoryPage(page)

    previous_loaded_page_movies_title_list = []


    with allure.step("Open application with default url"):
        #get the response data
        with page.expect_response(
                lambda response:
                "3/movie/popular" in response.url
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

    with allure.step("Validate the last page number in UI match with api response total_pages"):
        #Validation of the response status code
        MovieAPIValidator.validate_status(response)

        #Validate the Url payload has page=1
        response_body = response.json()
        print(response.url.lower())
        last_page_no_api = str(response_body["total_pages"])
        last_page_no_ui = popularpage.get_last_page_number()
        assert last_page_no_ui == last_page_no_api, f"Last page no in api:{last_page_no_api} not match with UI Last page no:{last_page_no_ui}"

    with allure.step("Click last page number and get the request"):
        # get the response data
        with page.expect_response(
                lambda response:
                "3/movie/popular" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_last_page_number_locator().click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {last_page_no_ui}",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step(
            f"Validate the page {last_page_no_ui} is default, response status code, payload contains 'page={last_page_no_ui}' and response has page={last_page_no_ui}"):
        page_no = last_page_no_ui
        # Validation of the response status code
        MovieAPIValidator.validate_status(response)

        # Validate the Url payload has Last page
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        # Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"

    with allure.step(f"Validate the page {last_page_no_ui} is select in UI and get the list of movie title"):
        # Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == page_no, f"The selected page number is not match with api page number"

        # store the page 1 movie list in loaded_page_movies_title_list
        previous_loaded_page_movies_title_list = [(card["title"], card["image_url"]) for card in
                                                  popularpage.get_movie_cards()]

    with allure.step(f"Click on the page {int(last_page_no_ui)-1} and validated the page {int(last_page_no_ui)-1} is selected in UI"):
        page_no=f"{int(last_page_no_ui)-1}"
        with page.expect_response(
                lambda response:
                "3/movie/popular" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_page_locator_with_page_no(page_no).click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {int(last_page_no_ui)-1}",
            attachment_type=allure.attachment_type.PNG
        )
        # Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == page_no, f"The selected page number is not match with api page number"

    with allure.step(f"Validate the page {int(last_page_no_ui)-1} response status code, payload contains 'page={int(last_page_no_ui)-1}' and response has page=2"):
        #Validation of the response status code
        MovieAPIValidator.validate_status(response)

        #Validate the Url payload has page=1
        response_body = response.json()
        reqest_payload = response.url
        payload_dict = MovieAPIValidator.request_payload(reqest_payload)
        assert payload_dict["page"] == page_no, f"Page no:{page_no} not found in the request payload"

        #Validate the api response has page=1
        assert response_body["page"] == int(page_no), f"Page no:{page_no} not found in the api response data"

        with allure.step(f"Get the Movie title list and validate page {int(last_page_no_ui)-1} movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_2_movies_title_list = [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_2_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page {int(last_page_no_ui)-1} and previous page movies titles list:{common_movie_title}"
            previous_loaded_page_movies_title_list.extend(page_2_movies_title_list)

    with allure.step(f"Click on the page {int(last_page_no_ui)-2} and validated the page {int(last_page_no_ui)-2} is selected in UI"):
        page_no=int(last_page_no_ui)-2
        print(page_no)
        with page.expect_response(
                lambda response:
                "3/movie/popular" in response.url
                and response.request.method == "GET"
        ) as response_info:
            popularpage.get_page_locator_with_page_no(page_no).click()
            page.wait_for_timeout(1000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {int(last_page_no_ui)-2}",
            attachment_type=allure.attachment_type.PNG
        )
        # Get the selected page number
        selected_page_no = popularpage.get_selected_page_number()
        assert selected_page_no == str(page_no), f"The selected page number is not match with api page number"

        with allure.step(f"Get the Movie title list and validate page {int(last_page_no_ui)-2} movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_3_movies_title_list = [(card["title"],card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_3_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page {int(last_page_no_ui)-2} and previous page movies titles list:{common_movie_title}"
            previous_loaded_page_movies_title_list.extend(page_3_movies_title_list)

    with (allure.step(f"Validate the page {int(last_page_no_ui)-3} is available in UI and able to click on the page {int(last_page_no_ui)-3}")):
        page_no=int(last_page_no_ui)-3
        page_4_locator = popularpage.page_section_locator.get_by_role("button", name=f"Page {page_no}")
        expect(page_4_locator).to_be_visible(timeout=10000)
        page_4_locator.click()
        page.wait_for_timeout(1000)
        popularpage.loading_icon_locator = page.get_by_label("audio-loading")
        allure.attach(
            page.screenshot(type="png"),
            name=f"Screenshot of the page {int(last_page_no_ui)-3}",
            attachment_type=allure.attachment_type.PNG
        )

        with allure.step(
                "Get the Movie title list and validate page 4 movies titles shouldn't be present in previous_loaded_page_movies_title_list"):
            page_4_movies_title_list = [(card["title"], card["image_url"]) for card in popularpage.get_movie_cards()]
            common_movie_title = list(set(page_4_movies_title_list) & set(previous_loaded_page_movies_title_list))
            assert not common_movie_title, f"Movie title present in page 4 and previous page movies titles list:{common_movie_title}"




