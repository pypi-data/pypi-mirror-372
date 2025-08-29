from pydantic import BaseModel


class PageRestructuringParameters(BaseModel):
    freshness_days: int
