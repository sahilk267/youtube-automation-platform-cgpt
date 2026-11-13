"""Strict M2 Studio V1 input shapes. Owner-authored timing, never fake alignment/verification."""
from typing import Literal
from pydantic import BaseModel, Field, model_validator, ConfigDict

class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid')

class Overlay(Strict):
    text: str = Field(min_length=1,max_length=110)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    anchor: Literal['TOP','CENTER','LOWER_THIRD'] = 'CENTER'
    style: Literal['LABEL','STAT','CALLOUT','IMAGE_INSERT'] = 'LABEL'
    image_asset_id: str|None=None
    @model_validator(mode='after')
    def positive(self):
        if self.end_ms<=self.start_ms:raise ValueError('Overlay end_ms must exceed start_ms')
        if (self.style=='IMAGE_INSERT') != (self.image_asset_id is not None):raise ValueError('IMAGE_INSERT requires image_asset_id')
        return self

class Visual(Strict):
    kind: Literal['ORIGINAL_DIAGRAM','SOLID','RIGHTS_APPROVED_STILL']='ORIGINAL_DIAGRAM'
    asset_id: str|None=None
    motion: Literal['STATIC','ILLUSTRATIVE_ROUTE']='STATIC'
    @model_validator(mode='after')
    def pair(self):
        if (self.kind=='RIGHTS_APPROVED_STILL') != (self.asset_id is not None):
            raise ValueError('Only RIGHTS_APPROVED_STILL requires an asset_id')
        return self

class Shot(Strict):
    role:Literal['HOOK','CONTEXT','EVIDENCE','EXPLANATION','PAYOFF','CTA']
    duration_ms:int=Field(ge=1200,le=12000)
    headline:str=Field(min_length=4,max_length=140)
    visual:Visual=Field(default_factory=Visual)
    overlays:list[Overlay]=Field(default_factory=list,max_length=5)
    claim_ids:list[str]=Field(default_factory=list,max_length=15)
    @model_validator(mode='after')
    def timing(self):
        for i,o in enumerate(self.overlays):
            if o.end_ms>self.duration_ms:raise ValueError('Overlay exceeds shot duration')
            for prior in self.overlays[:i]:
                if o.anchor==prior.anchor and o.start_ms<prior.end_ms and prior.start_ms<o.end_ms:
                    raise ValueError('Two overlays overlap in the same screen anchor')
        return self

class Caption(Strict):
    start_ms:int=Field(ge=0)
    end_ms:int=Field(gt=0)
    text:str=Field(min_length=1,max_length=160)
    @model_validator(mode='after')
    def timing(self):
        if self.end_ms<=self.start_ms:raise ValueError('Caption duration invalid')
        return self

class StudioPlanIn(Strict):
    locale:str=Field(pattern=r'^[a-z]{2}-[A-Z]{2}$')
    shots:list[Shot]=Field(min_length=2,max_length=12)
    captions:list[Caption]=Field(default_factory=list,max_length=75)
    captions_provenance:Literal['NOT_PROVIDED','OWNER_TIMED','SEGMENT_TIMED_MEASURED']='NOT_PROVIDED'
    music_asset_id:str|None=None
    locale_reviewed:bool=False
    @model_validator(mode='after')
    def validate_global(self):
        total=sum(s.duration_ms for s in self.shots)
        if total>90000:raise ValueError('CPU prototype limited to 90 seconds')
        last=0
        for c in self.captions:
            if c.start_ms<last:raise ValueError('Captions must be sorted and non-overlapping')
            if c.end_ms>total:raise ValueError('Caption extends beyond video')
            last=c.end_ms
        if (self.captions_provenance!='NOT_PROVIDED') != bool(self.captions):
            raise ValueError('Caption provenance must identify actual timing; otherwise use NOT_PROVIDED')
        if self.shots[0].role!='HOOK' or self.shots[-1].role not in ('PAYOFF','CTA'):
            raise ValueError('Video must start with HOOK and end with PAYOFF or CTA')
        return self

class OwnerAssetIn(Strict):
    origin:str=Field(min_length=8,max_length=600)
    license_note:str=Field(min_length=12,max_length=700)
    rights_attested:bool
