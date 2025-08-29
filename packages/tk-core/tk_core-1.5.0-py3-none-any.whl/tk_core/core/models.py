"""
This model validates the inputs for our Audit Table. Each of these fields are populated to
better understand and track requests that come in from our users
"""

import datetime as dt

from pydantic import BaseModel, Field


class AuditTableOutput(BaseModel):
    """
    Parameters:
    request_id: str
        -- generated prior to the pipeline running, normally generated in FastAPI
    request_time: dt.datetime
        -- the time the request was made, normally generated in FastAPI
    request_metadata: dict = Field(default={})
        -- the metadata from the request, passed in by users
    client_code: str | None = Field(default=None)
        -- the client code from the request, 'client_code' field in metadata
    consumer_application: str
        -- the application that made the request, 'consumer' field  in metadata
    processing_application: str
        -- the application that processed the request, what was the service
    cached_results: int | None = Field(default=None)
        -- the number of cached results generated in the pipeline itself
    needed_results: int | None = Field(default=None)
        -- the number of needed results generated in the pipeline itself
    errors: bool = False
        -- whether the request had errors defaults to False and is updated if needs be
    job_params: dict = Field(default={})
        -- the job parameters for the specific request
    """

    request_id: str
    request_time: dt.datetime
    request_metadata: dict = Field(default={})
    client_code: str | None = Field(default=None)
    consumer_application: str
    processing_application: str
    cached_results: int | None = Field(default=None)
    needed_results: int | None = Field(default=None)
    errors: bool = False
    job_params: dict = Field(default={})
