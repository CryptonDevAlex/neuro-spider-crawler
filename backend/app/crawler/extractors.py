from playwright.async_api import Page


async def extract_content(page: Page) -> dict[str, object]:
    raise NotImplementedError


async def extract_links(page: Page) -> list[str]:
    raise NotImplementedError


async def extract_tables(page: Page) -> list[dict[str, object]]:
    raise NotImplementedError
