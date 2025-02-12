from pydantic import BaseModel
from typing import List, Any , Optional


class Args(BaseModel):
    arg_name: str
    arg_value: Any
    is_static: bool


class MessageCreate(BaseModel):
    from_agent: str
    to_agent: str
    message: str
    args: List[Args]
    chain_id: str
    user_id: Optional[str]


class MessageOut(BaseModel):
    from_agent: str
    to_agent: str
    chain_id: str
    message: str
    args: List[Args]
    class Config:
        orm_mode = True
