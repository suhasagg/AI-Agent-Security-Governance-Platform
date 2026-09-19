from pydantic import BaseModel,Field
from typing import Literal,Any
class Identity(BaseModel):
    subject:str
    tenant_id:str
    roles:list[str]
class AgentRequest(BaseModel):
    message:str=Field(min_length=1,max_length=50000)
class PolicyRequest(BaseModel):
    tool:str
    arguments:dict[str,Any]
class Decision(BaseModel):
    effect:Literal["allow","deny","approval"]
    reason:str
    risk:Literal["low","medium","high","critical"]
class ApprovalRequest(BaseModel):
    tool:str
    arguments:dict[str,Any]
    ttl_seconds:int=Field(default=600,ge=60,le=3600)
