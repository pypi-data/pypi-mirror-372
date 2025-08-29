from pydantic.main import BaseModel


class GPS(BaseModel):
	latitude: float
	longitude: float
