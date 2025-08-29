import os

import serpapi
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout
from retry import retry

from tk_core.common.timeout import timeout
from tk_core.serp_api.models import SERPAPIProperRequestParameters, SERPAPITrendsSearchParameters

load_dotenv()

SNOWFLAKE_TABLE_MAP = {
    "google": "SERP_API_SERP_CACHE",
    "google_trends": "SERP_API_TRENDS_CACHE",
}


class SERPAPI:
    def __init__(
        self,
        api_key: str | None = os.environ.get("SERP_API_KEY"),
        engine: str = "google",
        params: SERPAPIProperRequestParameters | SERPAPITrendsSearchParameters | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
        Initializes the SERPAPI class
        Args:
            api_key (str | None, optional): The API Key for the serpapi client. Defaults to os.environ.get("SERP_API_KEY").
            engine (str, optional): The search engine to use. Defaults to "google".
                                        For more options see https://serpapi.com/search-api.
            params (TerakeetRequestModel | None, optional): The parameters for the search. Defaults to None.
                                        For more details see the specific endpoint documentation.
            metadata (TerakeetMetadata | None, optional): The metadata for the request. Defaults to None.
        """
        # validate API Key
        self.api_key: str = api_key
        if self.api_key is None:
            raise ValueError("SERP_API_KEY is not set as an environment variable or passed as an argument.")

        # Validate Params
        self.params: SERPAPIProperRequestParameters | SERPAPITrendsSearchParameters | None = params
        if self.params is None:
            raise ValueError("You must supply params for your request.")

        # Validate Metadata
        self.metadata: dict | None = metadata
        # if it isn't passed indirectly
        if self.metadata is None:
            raise ValueError("You must supply metadata for your request.")

        # initialize the engine, client and json_response
        self.engine: str = engine
        self._client: serpapi.Client | None = None
        self.json_response: dict | None = {}

    def create_client(self) -> serpapi.Client:
        """
        Creates a new serpapi client
        """
        return serpapi.Client(api_key=self.api_key)

    @property
    def client(self) -> serpapi.Client:
        """
        Returns the serpapi client as property
        """
        if self._client is None:
            self._client = self.create_client()
        return self._client

    @retry(exceptions=(HTTPError, Timeout), tries=3, delay=2, backoff=2)
    @timeout(10)
    def _make_request(self) -> dict:
        """
        Makes a request to the serpapi client
        Returns:
            dict: The response from the serpapi client
        """
        # print(f"Making request to SERPAPI.\nEngine: {self.engine}\nParams: {self.params}")
        params = self.params.model_dump()
        response = self.client.search(engine=self.engine, params=params)
        return response.data
