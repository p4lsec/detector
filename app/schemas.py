from pydantic import BaseModel
from typing import List

class IPList(BaseModel):
    ips: List[str]