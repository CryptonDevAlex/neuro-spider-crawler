from typing import Self

from playwright.async_api import Browser, Playwright, async_playwright


class BrowserSession:
    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    async def __aenter__(self) -> Self:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self.browser is not None:
            await self.browser.close()
        if self.playwright is not None:
            await self.playwright.stop()
