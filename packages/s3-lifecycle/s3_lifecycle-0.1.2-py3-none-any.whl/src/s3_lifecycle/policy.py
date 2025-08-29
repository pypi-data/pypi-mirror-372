from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, model_validator


class Transition(BaseModel):
    Date: Optional[str] = None  # ISO format string or datetime
    Days: Optional[int] = None
    StorageClass: str

    @model_validator(mode="after")
    def check_date_or_days(cls, values):
        if not values.Date and values.Days is None:
            raise ValueError("Either Date or Days must be provided")
        return values


class NoncurrentVersionTransition(BaseModel):
    NoncurrentDays: int
    StorageClass: str


class NoncurrentVersionExpiration(BaseModel):
    NoncurrentDays: int


class Expiration(BaseModel):
    Days: Optional[int] = None
    Date: Optional[str] = None


class Filter(BaseModel):
    Prefix: Optional[str] = None
    # Extend later for Tag-based filters


class Rule(BaseModel):
    ID: str
    Filter: Dict[str, Any]
    Status: str
    Transitions: Optional[List[Union[Transition, Dict[str, Any]]]] = None
    Expiration: Optional[Union[Expiration, Dict[str, Any]]] = None
    NoncurrentVersionTransitions: Optional[List[Union[NoncurrentVersionTransition, Dict[str, Any]]]] = None
    NoncurrentVersionExpiration: Optional[Union[NoncurrentVersionExpiration, Dict[str, Any]]] = None

    @model_validator(mode="after")
    def check_rule_not_empty(self):
        if (
                not self.Transitions
                and not self.Expiration
                and not self.NoncurrentVersionTransitions
                and not self.NoncurrentVersionExpiration
        ):
            raise ValueError(
                f"Rule '{self.ID}' must have at least one of: Transitions, Expiration, "
                "NoncurrentVersionTransitions, NoncurrentVersionExpiration"
            )
        return self


class LifecyclePolicy(BaseModel):
    Rules: List[Rule]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LifecyclePolicy":
        return cls.model_validate(d)
