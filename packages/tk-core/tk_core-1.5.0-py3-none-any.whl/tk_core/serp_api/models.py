from enum import Enum

from pydantic import BaseModel, Field


class SERPAPISearchParameters(BaseModel):
    """
    for parameter details please see https://serpapi.com/search-api
    """

    google_domain: str = Field(default="google.com")
    language: str = Field(default="en")
    country: str = Field(default="us")
    location: str = Field(default="United States")
    device: str = Field(default="desktop")
    per_page: int = Field(default=10)
    page_count: int = Field(default=1)
    engine: str = Field(default="google")
    freshness_days: int = Field(default=1)


class SERPAPIProperRequestParameters(BaseModel):
    q: str
    engine: str = Field(default="google")
    google_domain: str = Field(default="google.com")
    hl: str = Field(default="en")
    gl: str = Field(default="us")
    location: str = Field(default="United States")
    device: str = Field(default="desktop")
    num: int = Field(default=10)
    start: int = Field(default=0)


class SERPAPIDates(Enum):
    FIVE_YEARS = "today 5-y"
    ALL = "all"
    TWELVE_MONTHS = "today 12-m"
    NINETY_DAYS = "today 3-m"
    THIRTY_DAYS = "today 1-m"
    SEVEN_DAYS = "now 7-d"
    ONE_DAY = "now 1-d"
    FOUR_HOURS = "now 4-H"
    ONE_HOUR = "now 1-H"


class SERPAPITrendsSearchParameters(BaseModel):
    """
    for parameter details please see https://serpapi.com/google-trends-api
    """

    q: str
    date: SERPAPIDates = Field(default=SERPAPIDates.FIVE_YEARS.value)
    data_type: str = Field(default="TIMESERIES")
    geo: str = Field(default="")
    region: str = Field(default="")
    tz: str = Field(default="420")
    cat: int = Field(default=0)
    gprop: str = Field(default="")
    engine: str = Field(default="google_trends")
