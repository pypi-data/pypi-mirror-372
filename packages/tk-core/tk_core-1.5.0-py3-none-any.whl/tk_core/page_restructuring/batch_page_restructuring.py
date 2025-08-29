import logging
from datetime import datetime

from dotenv import load_dotenv

from tk_core.common.dates import datecode
from tk_core.core.batch_request import BatchRequest
from tk_core.core.tk_redis import TKRedis
from tk_core.page_restructuring.models import PageRestructuringParameters

load_dotenv()
logger = logging.getLogger(__name__)


class BatchPageRestructuring(BatchRequest):
    """
    Class for batch page restructuring API requests
    Diagram: https://lucid.app/lucidchart/f58847bf-cbac-4b46-8695-1625217acf81/edit
    """

    def __init__(self, urls: list, params: PageRestructuringParameters, metadata: dict):
        self.input_objects: list = urls
        self.job_params: PageRestructuringParameters = params
        # Convert the parameters into a dictionary representation.
        # We exclude 'freshness_days' from this process because it's not a factor in determining
        # if we have cached results that can be served within the given window.
        # Essentially, we want two identical requests with different 'freshness_days' values
        # to produce the same hash.
        self.memoized_params = self.job_params.model_dump()
        del self.memoized_params["freshness_days"]
        self.metadata: dict = metadata
        self.freshness_days = params.freshness_days
        self.input_objects_name = "url"
        # validate freshness_days
        if self.freshness_days not in [0, 1, 30]:
            logger.error(f"incorrect freshness_day sprovided: {self.freshness_days}")
            raise ValueError("freshness_days (days) must be 0, 1, or 30")
        self.run_date = int(datecode())
        self.executed_at = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        self.indv_request_hash = None
        self.execution_id = None
        self.uri = None
        self.batch_execution_uuid = None
        self.created_by = "tk_core_page_restructuring"
        self.minimum_date = self.run_date - self.freshness_days
        # create redis object
        self.redis = TKRedis()
        self.invalid_urls = []
