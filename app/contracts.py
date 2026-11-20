from typing import Literal
from pydantic import BaseModel,Field,ConfigDict,model_validator
class Strict(BaseModel):model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class PlanInput(Strict):
    faculty_id:str
    cycle:Literal['2025-26']='2025-26'
    profile:Literal['balanced','teaching','research','administrative']='balanced'
    request:str=Field(min_length=10,max_length=2000)
    completeness:dict[str,str]
    policy_id:str
class Rule(Strict):
    kind:str=Field(min_length=2,max_length=80)
    category:Literal['research','teaching','administrative']
    method:Literal['count','sum','mean','weighted_mean']
    weight:float=Field(ge=0,le=10000)
    divisor:float=Field(gt=0,le=10000,default=1)
    cap:float=Field(ge=0,le=10000)
    citation:str=Field(min_length=3,max_length=500)
class Band(Strict):
    minimum:float=Field(ge=0,le=100000)
    label:str=Field(min_length=1,max_length=100)
class PolicyInput(Strict):
    name:str=Field(min_length=3,max_length=120)
    cycle:Literal['2025-26']='2025-26'
    profile:Literal['balanced','teaching','research','administrative']='balanced'
    source_id:str
    reference:str=Field(min_length=5,max_length=500)
    rules:list[Rule]=Field(min_length=1,max_length=40)
    bands:list[Band]=Field(min_length=1,max_length=15)
    @model_validator(mode='after')
    def unique(self):
        if len({r.kind for r in self.rules})!=len(self.rules):raise ValueError('Rule kinds must be unique.')
        if len({r.minimum for r in self.bands})!=len(self.bands) or min(r.minimum for r in self.bands)!=0:raise ValueError('Rating bands need unique boundaries, including zero.')
        return self
class ActivityInput(Strict):
    faculty_id:str
    category:Literal['research','teaching','administrative']
    kind:str=Field(min_length=2,max_length=80)
    title:str=Field(min_length=5,max_length=500)
    value:float=Field(ge=0,le=10000000)
    date:str
    students:int|None=Field(default=None,ge=0,le=1000000)
    source_id:str
    locator:str=Field(min_length=3,max_length=500)
class Decision(Strict):
    action:Literal['approve','return','override']
    note:str=Field(min_length=5,max_length=2000)
    rating_override:str|None=None
class EvidenceDecision(Strict):
    status:Literal['verified','excluded','flagged']
    note:str=Field(min_length=5,max_length=2000)
