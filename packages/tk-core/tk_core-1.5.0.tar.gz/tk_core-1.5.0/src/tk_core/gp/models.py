from pydantic import BaseModel


class GrowthProjectionsParameters(BaseModel):
    gp_request: dict = {}
