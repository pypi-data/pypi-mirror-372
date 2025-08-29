from pydantic import BaseModel, Field

from tk_core.page_restructuring.models import PageRestructuringParameters
from tk_core.page_scrape.models import ScrapingBeeParameters
from tk_core.serp_api.models import SERPAPISearchParameters


class TamParameters(BaseModel):
    tam_id: str


class GenericAsyncRequest(BaseModel):
    job_name: str
    metadata: dict
    job_params: dict | SERPAPISearchParameters | TamParameters | ScrapingBeeParameters | PageRestructuringParameters
    input_objects: list | str | None = Field(default=None)


class GenericAsyncResponse(BaseModel):
    job_name: str
    metadata: dict
    job_info: dict | None = Field(default=None)
    job_status: str
    traceback: str | None = Field(default=None)
