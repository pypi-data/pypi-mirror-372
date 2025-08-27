"""
playwright test sample

run test：
> pytest --browser=chromium --headed -vs test_web.py
"""
import re
import time

from playwright.sync_api import Page, expect


def test_has_title(page: Page, base_url):
    page.goto(base_url)

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Bing"))


def test_get_started_link(page: Page, base_url):
    page.goto(base_url)
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    input = page.locator("#sb_form_q")
    input.type("playwright")
    input.press("Enter")
    time.sleep(5)

    # Expects page to have a heading with the name of "Fast and reliable end-to-end testing for modern".
    search_result = page.get_by_role("link", name='Fast and reliable end-to-end testing for modern').first
    expect(search_result).to_be_visible()
