from pytest_bdd import scenario, given, when, then, parsers
from tests.base_page import BasePage
import os

FEATURE_FILE = os.path.join(os.path.dirname(__file__), "../features/admin_search.feature")

@scenario(FEATURE_FILE, 'Search users with different roles')
def test_differentUser_search():
    """Bu fonksiyon boş kalır, @scenario dekoratörü işi yapar."""
    pass

@given('the user is on the OrangeHRM login page')
def go_to_login(bp):
    bp.goto_base_url()

@when(parsers.parse('the user logs in with "{user}" and "{password}"'))
def login(bp, user, password):
    bp.smart_fill("input[name='username']", user)
    bp.smart_fill("input[name='password']", password)
    bp.smart_click("button[type='submit']")

@when(parsers.parse('the user navigates to the "{menu}" section'))
def navigate_to_admin(bp, menu):
    bp.smart_click(f"text={menu}")

@when(parsers.parse('the user searches for role "{role}"'))
def search_role(bp, role):
    dropdown = bp.page.locator(".oxd-input-group").filter(has_text="User Role").locator(".oxd-select-wrapper")
    bp.smart_dropdown(dropdown, role)
    bp.smart_click("button[type='submit']")

@then(parsers.parse('the "{column_name}" column in the first row should contain "{expected_text}"'))
def verify_result(bp, column_name, expected_text):    
    target_cell = "div.oxd-table-card >> nth=0 >> div[role='cell'] >> nth=1"
    bp.assert_text_equals(target_cell, expected_text)