from playwright.async_api import async_playwright


async def playwright_page():
    """
    >>> page = await playwright_page()
    >>> response = await page.goto("https://www.google.com")
    >>> response.status
    """

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    return page
