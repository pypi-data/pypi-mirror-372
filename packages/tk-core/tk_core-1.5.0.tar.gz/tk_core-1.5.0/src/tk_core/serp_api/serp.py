"""Deals with crafting and executing requests to SerpApi"""

from tk_core.serp_api.base import SERPAPI
from tk_core.serp_api.models import SERPAPIProperRequestParameters


def get_serp_client(params: SERPAPIProperRequestParameters | dict, request_metadata: dict | None = None) -> SERPAPI:
    """Creates a new instance of the SERPAPI class"""
    # convert to pydantic model if dict
    if isinstance(params, dict):
        params = SERPAPIProperRequestParameters.model_validate(params)

    return SERPAPI(engine="google", params=params, metadata=request_metadata)
