from typing_extensions import TypeVar
from dataclasses import dataclass, field
from mexc.core.exc import ValidationError

T = TypeVar('T')

def validator(Type: type[T]):
  from pydantic import TypeAdapter
  adapter = TypeAdapter(Type)
  
  def validate(data: str | bytes | bytearray) -> T:
    from pydantic import ValidationError as PydanticValidationError
    try:
      return adapter.validate_json(data)
    except PydanticValidationError as e:
      raise ValidationError from e

  return validate

@dataclass
class ValidationMixin:
  default_validate: bool = field(default=True, kw_only=True)

  def validate(self, validate: bool | None) -> bool:
    return self.default_validate if validate is None else validate