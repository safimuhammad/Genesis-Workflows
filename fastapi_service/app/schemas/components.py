from pydantic import BaseModel
from typing import List


class ArgItem(BaseModel):
    arg_name: str
    arg_value: str
    example: str
    description: str
    is_static: bool


class Output(BaseModel):
    out_name: str
    out_value: str
    example: str
    description: str


class AbilityCreate(BaseModel):
    tool_name: str
    description: str
    args: List[ArgItem]
    output: List[Output]


class AbilityOut(BaseModel):
    tool_name: str
    description: str
    args: List[ArgItem]
    output: List[Output]

    class Config:
        orm_mode = True
