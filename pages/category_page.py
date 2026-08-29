from playwright.sync_api import Page, expect

class CategoryPage:
    #locator in init
    def __init__(self, page: Page):
        self.page = page
        self.category_element_locator = page.locator("header nav li")
        self.trend_tab_button_locator = page.locator('//a[text()="Trend"]')
        self.popular_tab_button_locator = page.locator('//a[text()="Popular"]')
        self.newest_tab_button_locator = page.locator('//a[text()="Newest"]')
        self.top_rated_tab_button_locator = page.locator('//a[text()="Top rated"]')
        self.page_section_locator = page.locator("#react-paginate")
        self.previous_button_locator = self.page_section_locator.get_by_text("Previous")
        self.next_button_locator = self.page_section_locator.get_by_text("Next")
        self.search_box_locator = self.page.get_by_placeholder("SEARCH")
        self.loading_icon_locator = self.page.get_by_label("audio-loading")
        self.type_dropdown_locator = page.locator(
            "//p[normalize-space()='Type']"
            "/following-sibling::div[1]//input")
        self.get_type_dropdown_locator = page.locator(
            "//p[normalize-space()='Type']"
            "/following-sibling::div[1]")

        self.min_year_dropdown_locator = page.locator(
            "//p[normalize-space()='Year']"
            "/following-sibling::div[1]//input").first
        self.max_year_dropdown_locator = page.locator(
            "//p[normalize-space()='Year']"
            "/following-sibling::div[1]//input").nth(1)

        self.rating_position_locator = page.locator("div[role='radio'][aria-posinset='4'] > div:nth-child(2)")
        self.genre_dropdown_locator = page.locator(
            "//p[normalize-space()='Genre']"
            "/following-sibling::div[1]//input")

    def get_previous_button_locator(self):
        return self.page_section_locator.get_by_text("Previous")

    def get_next_button_locator(self):
        return self.page_section_locator.get_by_text("Next")

    def get_break_page_button_locator(self):
        self.page_section_locator = self.page.locator("#react-paginate")
        return self.page_section_locator.locator("li.break")

    def get_last_page_number(self):
        return self.get_last_page_number_locator().inner_text()

    def get_last_page_number_locator(self):
        return self.next_button_locator.locator("xpath=./ancestor::li").locator("xpath=./preceding-sibling::li[1]")


    def get_selected_page_number(self):
        return self.page_section_locator.locator("li.selected").inner_text()

    def get_page_locator_with_page_no(self,page_no):
        return self.page_section_locator.get_by_label(f"Page {page_no}")

    def get_movie_cards(self):
        card_list_locator = self.page.locator(
            "div.grid > div:has(img[alt='Movie Poster'])"
        )
        cards = card_list_locator

        movies = []

        for index in range(cards.count()):
            card = cards.nth(index)

            paragraphs = card.locator("p")

            title = paragraphs.nth(0).inner_text().strip()
            metadata = paragraphs.nth(1).inner_text().strip()
            image_url = card.locator("img[alt='Movie Poster']").get_attribute("src")

            genre, year = metadata.rsplit(",", 1)

            # print(f"Title: {title}, Genre: {genre}, Year: {year}, Image URL: {image_url}")
            movies.append({
                "title": title,
                "genre": genre.strip(),
                "year": int(year.strip()) if year.strip() != "NaN" else 0,
                "image_url": image_url
            })

        return movies

    def search_text(self, search_term: str):
        self.search_box_locator.fill(search_term)
        self.search_box_locator.press("Enter")
        self.page.wait_for_timeout(2000)
        self.loading_icon_locator = self.page.get_by_label("audio-loading")
        expect(self.loading_icon_locator).to_be_hidden(timeout=10000)

    def select_type(self, type_name: str):
        self.type_dropdown_locator.fill(type_name)
        self.type_dropdown_locator.press("Enter")

    def select_min_year(self, min_year: str):
        self.min_year_dropdown_locator.fill(min_year)
        self.min_year_dropdown_locator.press("Enter")

    def select_max_year(self, max_year: str):
        self.max_year_dropdown_locator.fill(max_year)
        self.max_year_dropdown_locator.press("Enter")
        self.page.wait_for_timeout(1000)

    def select_genre(self, genre: str):
        self.genre_dropdown_locator.fill(genre)
        self.genre_dropdown_locator.press("Enter")
        self.page.wait_for_timeout(1000)

    # def login(self, username: str, password: str):
    #     self.username.fill(username)
    #     self.password.fill(password)
    #     self.login_button.click()
