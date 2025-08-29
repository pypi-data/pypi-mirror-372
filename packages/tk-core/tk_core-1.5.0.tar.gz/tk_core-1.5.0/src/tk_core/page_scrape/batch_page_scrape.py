import datetime

from scrapingbee import ScrapingBeeClient

from tk_core.common.dates import datecode
from tk_core.core.batch_request import BatchRequest
from tk_core.core.tk_redis import TKRedis
from tk_core.page_scrape.models import ScrapingBeeParameters
from tk_core.page_scrape.scraping_bee import get_api_key


def get_execution_id(request_hash: str | None = None, run_date: int = int(datecode())) -> str:
    """
    returns the execution id for a hash
    """
    return f"{request_hash}/{run_date}"


class BatchPageScrape(BatchRequest):
    SOURCE_NAME_AND_VERSION = "tk_core_scraping_bee_batch_initiator"

    def __init__(self, urls: list, params: ScrapingBeeParameters, metadata: dict):
        self.input_objects: list = urls
        self.job_params: ScrapingBeeParameters = params
        # create a dictionary version of the parameters
        # remove freshness_days as it isn't a variable we want to consider
        # when checking if we have cached results we can serve within the window provided
        self.memoized_params = self.job_params.model_dump()
        del self.memoized_params["freshness_days"]
        self.metadata: dict = metadata
        self.freshness_days = params.freshness_days
        self.input_objects_name = "url"
        # validate freshness_days
        if self.freshness_days not in [0, 1, 30]:
            raise ValueError("freshness_days (days) must be 0, 1, or 30")

        self.run_date = int(datecode())
        self.executed_at = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        self.indv_request_hash = None
        self.execution_id = None
        self.uri = None
        self.batch_execution_uuid = None
        self.created_by = "tk_core_batch_page_scraper_executor"
        self.minimum_date = self.run_date - self.freshness_days
        self.redis = TKRedis()
        self.api_key = get_api_key()
        self.SB = ScrapingBeeClient(api_key=self.api_key)
        self.invalid_urls = []
