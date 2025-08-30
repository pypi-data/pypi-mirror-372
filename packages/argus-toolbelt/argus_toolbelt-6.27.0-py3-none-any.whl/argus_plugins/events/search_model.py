from enum import Enum

from argus_api.exceptions.http import ObjectNotFoundException
from argus_plugins.cases.utils import get_customer_id
from argus_plugins.enrichments import EVENTS_ENRICHMENTS
from argus_plugins.events.utils import FLAGS, SEVERITIES
from pydantic import BaseModel, validator
from pydantic.typing import Dict, List, Optional, Union

FlagEnum = Enum("FlagEnum", {f: f for f in FLAGS})
SeverityEnum = Enum("SeverityEnum", {s: s for s in SEVERITIES})
EnrichEnum = Enum("EnrichEnum", {e: e for e in EVENTS_ENRICHMENTS})


class IncludeExcludeStrings(BaseModel):
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None


class IncludeExcludeInts(BaseModel):
    include: Optional[List[int]] = None
    exclude: Optional[List[int]] = None


class IncludeExcludeCustomers(IncludeExcludeStrings):
    include: Optional[List[Union[str, int]]] = None
    exclude: Optional[List[Union[str, int]]] = None

    @validator("include", "exclude", each_item=True)
    def get_customer_id(cls, v):
        if v is None:
            return None
        try:
            return get_customer_id(v)
        except ObjectNotFoundException:
            raise ValueError(f'customer "{v}" not found')


class IncludeExcludeProps(BaseModel):
    include: Optional[Dict[str, str]] = None
    exclude: Optional[Dict[str, str]] = None


class IPSearchOptions(BaseModel):
    any: Optional[IncludeExcludeStrings] = None
    source: Optional[IncludeExcludeStrings] = None
    destination: Optional[IncludeExcludeStrings] = None


class SearchOptions(BaseModel):
    """pydantic model of the events search command options."""

    customer: Optional[IncludeExcludeCustomers] = None
    flag: Optional[IncludeExcludeStrings] = None
    alarm: Optional[IncludeExcludeStrings] = None
    signature: Optional[IncludeExcludeStrings] = None
    properties: Optional[IncludeExcludeProps] = None
    attack_category_id: Optional[IncludeExcludeInts] = None
    ip: Optional[IncludeExcludeStrings] = None
    source_ip: Optional[IncludeExcludeStrings] = None
    destination_ip: Optional[IncludeExcludeStrings] = None

    exact_match_properties: bool = True
    min_severity: SeverityEnum = SeverityEnum.high
    min_count: Optional[int] = None
    source_ip_min_bits: Optional[int] = None
    destination_ip_min_bits: Optional[int] = None
    enrich: Optional[List[EnrichEnum]] = None

    class Config:
        use_enum_values = True

    def get_include_arg(
        self,
        arg_name,
    ):

        field = getattr(self, arg_name, None)
        return {
            f"include_{arg_name}": field.include if field else None,
            f"exclude_{arg_name}": field.exclude if field else None,
        }

    def to_search_args(self):

        include_exclude_fields = (
            "properties",
            "flag",
            "alarm",
            "signature",
            "attack_category_id",
            "ip",
            "source_ip",
            "destination_ip",
            "customer",
        )
        args = self.dict(exclude=set(include_exclude_fields))
        for thing in include_exclude_fields:
            args.update(self.get_include_arg(thing))
        return args
