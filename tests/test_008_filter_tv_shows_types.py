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
@allure.feature("Filter TV Shows Types")
def test_008_filter_tv_shows_types(page: Page, settings):
    #page initialization
    popularpage = CategoryPage(page)

    with allure.step("Open application "):
        #goto landing page(popular)
        page.goto("/")
        page.wait_for_load_state("networkidle")

    with allure.step("select TV Shows Type and validate tv api response status, schema"):
        #Select api contains movie
        with page.expect_response(
                lambda response:
                "tv" in response.url.lower()
        ) as response_info:
            popularpage.select_type("TV Shows")
            page.wait_for_timeout(2000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)

        response = response_info.value

        #Validation of the response status code
        MovieAPIValidator.validate_status(response)
        response_body = response.json()

        # Response schema validation
        MovieAPIValidator.validate_response_structure(
            response_body
        )
        for tv in response_body["results"]:
            MovieAPIValidator.validate_tv_schema(tv)

    with allure.step("Validation of TV list and TV details"):
        card_details = popularpage.get_movie_cards()
        assert len(card_details) > 0, "There is no tv card in the popular page"
        allure.attach(
            f"The TV card details: {str(card_details)}\n"
            f"The count of the TV card details: {str(len(card_details))}",
            name="Details of the category",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(
            page.screenshot(type="png"),
            name="Screenshot of the TV Shows type selected",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Validation of UI tv card title match the api tv title"):
        api_tv_title = [tv["name"] for tv in response_body["results"]]
        ui_tv_title = [card["title"] for card in card_details]
        assert api_tv_title == ui_tv_title, "The tv card order does not match the api response"

    with allure.step("click on the trend and validate the type is selected 'tv' and api response url contains 'tv'"):
        with page.expect_response(
                lambda response:
                "tv" in response.url.lower()
        ) as response_info:
            popularpage.trend_tab_button_locator.click()
            page.wait_for_timeout(2000)
            popularpage.loading_icon_locator = page.get_by_label("audio-loading")
            expect(popularpage.loading_icon_locator).to_be_hidden(timeout=10000)
        response = response_info.value

        # Validation of the response status code
        MovieAPIValidator.validate_status(response)
        response_body = response.json()

        # Response schema validation
        MovieAPIValidator.validate_response_structure(
            response_body
        )
        for tv in response_body["results"]:
            MovieAPIValidator.validate_tv_schema(tv)

        with allure.step("Validation of Type option is 'TV Shows'"):
            expect(popularpage.get_type_dropdown_locator).to_have_text("TV Shows",use_inner_text=True)
            allure.attach(
                f"The selected type: {str(popularpage.get_type_dropdown_locator.inner_text())}",
                name="Details of the selected type",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validation of Latest trend tv card title should match previous popular tv card title"):
            card_details = popularpage.get_movie_cards()
            ui_trend_tv_title = [card["title"] for card in card_details]
            assert ui_trend_tv_title != ui_tv_title, "The movie card is not reloaded with trend category"
