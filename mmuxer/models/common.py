from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError

from mmuxer.utils import ParseException


class BaseModel(PydanticBaseModel):
    class Config:
        extra = "forbid"

    @classmethod
    def parse_data(cls, data):
        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise ParseException.from_validation_error(
                exc=exc,
                full_content=data,
            )
