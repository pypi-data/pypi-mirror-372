"""Access the Google SERPAPI API via SERP API."""

from tk_core.serp_api.models import SERPAPITrendsSearchParameters
from tk_core.serp_api.serp import SERPAPI


def get_trend_client(params: SERPAPITrendsSearchParameters | dict, request_metadata: dict | None = None) -> SERPAPI:
    """Creates a new instance of the SERPAPI class"""
    # convert to pydantic model if dict
    if isinstance(params, dict):
        params = SERPAPITrendsSearchParameters.model_validate(params)

    return SERPAPI(engine="google_trends", params=params, metadata=request_metadata)
