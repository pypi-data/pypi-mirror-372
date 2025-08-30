from typing import List

from pydantic.main import BaseModel
from pydantic.fields import Field


class DeliveryService(BaseModel):
	id: int
	name: str


class Result(BaseModel):
	delivery_services: List[DeliveryService] = Field(default_factory=list, validation_alias="deliveryService")


class Response(BaseModel):
	result: Result = Field(default_factory=Result)
