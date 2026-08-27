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

            movies.append({
                "title": title,
                "genre": genre.strip(),
                "year": int(year.strip()),
                "image_url": image_url
            })

        return movies

    def search_text(self, search_term: str):
        self.search_box_locator.fill(search_term)
        self.search_box_locator.press("Enter")
        self.page.wait_for_timeout(2000)
        self.loading_icon_locator = self.page.get_by_label("audio-loading")
        expect(self.loading_icon_locator).to_be_hidden(timeout=10000)


    # def login(self, username: str, password: str):
    #     self.username.fill(username)
    #     self.password.fill(password)
    #     self.login_button.click()
