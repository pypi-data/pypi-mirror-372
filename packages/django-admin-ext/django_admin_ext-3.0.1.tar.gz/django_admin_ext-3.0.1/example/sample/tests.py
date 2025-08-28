import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from playwright.sync_api import sync_playwright, expect


class PlayWrightAjaxAdminTests(StaticLiveServerTestCase):
    fixtures = ['initial_data.json']

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.login()

    def tearDown(self):
        self.page.close()

    def login(self):
        self.page.goto(f"{self.live_server_url}/admin/")
        self.page.wait_for_selector('text=Django administration')
        self.page.fill('[name=username]', 'admin')
        self.page.fill('[name=password]', 'test')

        self.page.get_by_role("button", name="Log in").click()
        expect(self.page.locator('#content h1')).to_have_text("Site administration")

    def assert_selected_option(self, selector, value):
        """Asserts that the selected element has the given text value selected."""
        # Find the option by its text to get its 'value' attribute
        option_value = self.page.locator(f"{selector} option:has-text('{value}')").get_attribute("value")
        expect(self.page.locator(selector)).to_have_value(option_value)

    def assert_select_has_options(self, selector, expected_options):
        """Asserts that a select element contains the exact list of option texts."""
        expect(self.page.locator(f"{selector} option")).to_have_text(expected_options)

    def change_page_selection(self, selector, value):
        self.page.select_option(selector, label=value)

    def test_main_ingredient_element_not_present_initially(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.assertEqual(1, self.page.locator("#id_food_type").count())
        self.assertEqual(0, self.page.locator("#id_main_ingredient").count())

    def test_main_ingredient_element_shows_when_pizza_food_type_is_selected(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Pizza")
        expected_options = ['---------', 'pepperoni', 'mushrooms', 'beef', 'anchovies']
        self.assert_select_has_options("#id_main_ingredient", expected_options)

    def test_main_ingredient_element_shows_when_burger_food_type_is_selected(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Burger")
        expected_options = ['---------', 'mushrooms', 'beef', 'lettuce']
        self.assert_select_has_options("#id_main_ingredient", expected_options)

    def test_ingredient_details_is_shown_when_beef_is_selected(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Burger")
        self.change_page_selection("#id_main_ingredient", value="beef")

        expected_options = ['---------', 'Grass Fed', 'Cardboard Fed']
        self.assert_select_has_options("#id_ingredient_details", expected_options)

    def test_ingredient_details_is_reset_when_main_ingredient_changes(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Burger")
        self.change_page_selection("#id_main_ingredient", value="beef")

        expected_options = ['---------', 'Grass Fed', 'Cardboard Fed']
        self.assert_select_has_options("#id_ingredient_details", expected_options)

        # When an ingredient with no details is selected, the details field should disappear
        self.change_page_selection("#id_main_ingredient", value="lettuce")
        expect(self.page.locator("#id_ingredient_details")).to_have_count(0)

    def test_ingredient_details_change_when_main_ingredient_changes(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Pizza")
        self.change_page_selection("#id_main_ingredient", value="beef")

        expected_options = ['---------', 'Grass Fed', 'Cardboard Fed']
        self.assert_select_has_options("#id_ingredient_details", expected_options)

        self.change_page_selection("#id_main_ingredient", value="pepperoni")
        expected_options = ['---------', 'Grass Fed Goodness', 'Cardboard Not So Goodness']
        self.assert_select_has_options("#id_ingredient_details", expected_options)

    def test_main_ingredient_does_not_change_when_food_type_changes_if_valid_option(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Pizza")
        self.change_page_selection("#id_main_ingredient", value="beef")

        self.assert_selected_option("#id_main_ingredient", "beef")

        self.change_page_selection("#id_food_type", value="Burger")
        self.assert_selected_option("#id_main_ingredient", "beef")

    def test_shows_dynamic_field_on_existing_instance(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/1/")
        self.assert_selected_option('#id_main_ingredient', 'anchovies')

    def test_sets_ingredient_details_when_available(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Burger")
        self.change_page_selection("#id_main_ingredient", value="beef")
        self.change_page_selection("#id_ingredient_details", value="Grass Fed")

        self.page.click('input[name="_continue"]')
        self.assert_selected_option('#id_ingredient_details', 'Grass Fed')

    def test_allows_changing_dynamic_field_on_existing_instance(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        # create new meal
        self.change_page_selection("#id_food_type", value="Burger")
        self.change_page_selection("#id_main_ingredient", value="mushrooms")
        self.page.click('input[name="_continue"]')

        # change main_ingredient for new meal
        self.change_page_selection("#id_main_ingredient", value="lettuce")
        self.page.click('input[name="_continue"]')

        # make sure there are no errors
        expect(self.page.locator(".errors")).to_have_count(0)

        # make sure our new main_ingredient was saved
        self.assert_selected_option('#id_main_ingredient', 'lettuce')

        # delete our meal when we're done
        self.page.click('a[class="deletelink"]')
        self.page.click('[type="submit"]')

    def test_gives_field_required_error_when_dynamic_field_not_chosen(self):
        self.page.goto(f"{self.live_server_url}/admin/sample/meal/add/")

        self.change_page_selection("#id_food_type", value="Burger")

        self.page.click('input[name="_save"]')

        msg = 'This field is required.'
        expect(self.page.locator('.errors.field-main_ingredient li')).to_have_text(msg)
