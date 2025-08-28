from pydantic import Field
from ..base import SingularBaseModel
from typing import List, Literal, Optional
from datetime import datetime
from ..dsp.v2025_1_rc2.low_level import Offer

class InternalError(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["InternalError"] = Field(alias="@type")
    code: Optional[str] = None
    reason: Optional[List] = None

class ConnectionError(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ConnectionError"] = Field(alias="@type")
    code: Optional[str] = None
    reason: Optional[List] = None

class Asset(SingularBaseModel):
    id: str
    name: str
    offer_id: Optional[List[str]]= None
    description: Optional[str] = None
    organization: Optional[str] = None
    tags: Optional[List[str]] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

class Contact(SingularBaseModel):
    id: str = Field(alias="_id")
    preferred_name: str
    base_url: str
    version: str
    prefix: str


class ExtendedOffer(SingularBaseModel):
    id: str = Field(alias="_id")
    preferred_name: str
    reference_dataset_id: str = None
    offer: Offer