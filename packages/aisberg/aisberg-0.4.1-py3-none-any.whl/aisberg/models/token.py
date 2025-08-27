from typing import List

from pydantic import BaseModel


class TokenInfo(BaseModel):
    message: str
    id: str
    username: str
    email: str
    groups: List[str]
    roles: List[str]
