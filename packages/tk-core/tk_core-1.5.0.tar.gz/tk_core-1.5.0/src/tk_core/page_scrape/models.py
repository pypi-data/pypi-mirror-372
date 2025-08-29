from pydantic import BaseModel


class ScrapingBeeParameters(BaseModel):
    render_js: bool = True
    js_scenario: dict = {}
    screenshot: bool = False
    screenshot_full_page: bool = False
    premium_proxy: bool = False
    return_page_source: bool = True
    freshness_days: int = 0
