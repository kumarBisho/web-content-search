# models/schemas.py
from pydantic import BaseModel

class SearchRequest(BaseModel):
    url: str
    query: str
