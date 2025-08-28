import json
import typing
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Tuple, Type, TypeVar, get_type_hints

import asyncpg
import pydantic
from aiohttp.web import HTTPError, HTTPNotFound, HTTPSuccessful

from alxhttp.req_id import get_request, get_request_id
from alxhttp.typescript.type_checks import TypeType, is_dict, is_list, is_model_type, is_optional, is_union_of_models
from alxhttp.typescript.types import TSEnum


def recursive_json_loads(type: TypeType, data) -> Any:
  """
  json loads anything that requires recursive model verification
  """

  # Unwrap optionals
  if is_optional(type):
    targs = typing.get_args(type)
    return recursive_json_loads(targs[0], data)

  if is_union_of_models(type):
    # TODO: stronger checking on the union models
    if isinstance(data, str):
      return json.loads(data)
    elif isinstance(data, dict):
      return data
    else:
      assert False

  if isinstance(data, str) and (is_dict(type) or is_list(type) or is_model_type(type)):
    return recursive_json_loads(type, json.loads(data))

  if isinstance(data, dict):
    assert is_dict(type) or is_model_type(type)

    for k, v in data.items():
      if is_model_type(type):
        t = get_type_hints(type).get(k)
      else:
        assert is_dict(type)
        t = typing.get_args(type)[1]

      # likely a mistake with the model/record that will be caught by pydantic
      if not t:
        continue

      data[k] = recursive_json_loads(t, v)
  elif isinstance(data, list):
    assert is_list(type)
    type = typing.get_args(type)[0]
    data = [recursive_json_loads(type, d) for d in data]

  return data


BaseModelType = TypeVar('BaseModelType', bound='BaseModel')


def replace_datetime_values_with_timestamps(value: Dict | List) -> Dict | List:
  if isinstance(value, dict):
    for k, v in value.items():
      if isinstance(v, datetime):
        value[k] = v.timestamp()
      elif isinstance(v, dict) or isinstance(v, list):
        value[k] = replace_datetime_values_with_timestamps(v)
  elif isinstance(value, list):
    value = [replace_datetime_values_with_timestamps(v) for v in value]
  return value


class BaseModel(pydantic.BaseModel):
  """
  A Pydantic model with some opinions:
  - extra values are not allowed
  - datetimes are serialized as float timestamps
  """

  model_config = pydantic.ConfigDict(extra='forbid')

  @pydantic.field_serializer('*', mode='wrap')
  def datetimes_as_timestamps(self, value: Any, nxt: pydantic.SerializerFunctionWrapHandler) -> Any:
    if isinstance(value, datetime):
      return value.timestamp()
    elif isinstance(value, dict) or isinstance(value, list):
      return replace_datetime_values_with_timestamps(value)
    else:
      return nxt(value)

  @classmethod
  def from_record(cls: Type[BaseModelType], record: asyncpg.Record | None) -> BaseModelType:
    if not record:
      raise HTTPNotFound()
    record_dict = dict(record)
    record_dict = recursive_json_loads(cls, record_dict)
    return cls.model_validate(record_dict)

  def exception(self, status_code: int = 200):
    """
    Wrap the model in an exception that will render as JSON
    """
    return BaseModelException(self, status_code=status_code)


class Empty(BaseModel):
  pass


class ErrorModel(BaseModel):
  """
  Our base class for 4XX/5XX responses. 'error' is used to allow us to treat this as
  a discriminated union and switch on it in typescript.
  """

  error: str = 'HTTPBadRequest'
  status_code: int = 400
  request_id: Optional[str] = None

  def exception(self):
    """
    Wrap the model in an exception that will render as JSON

    Intentionally does not take a status_code argument. override it on your derived class instead
    """
    return ErrorModelException(self)


BaseModelType = TypeVar('BaseModelType', bound=BaseModel)


class BaseModelException[BaseModelType](HTTPSuccessful):
  """
  Pydantic models can't be used in mixin-inheritance so instead if we want to
  raise a model as an exception we have to store it inside a real exception.

  To help the type hinting work this is a generic class parameterized over
  your derived error type.
  """

  status_code: int = 200

  def __init__(self, model: BaseModelType, status_code: int = 200):
    self.model: BaseModel = model  # type: ignore | this is at the limits of python's type checker
    self.status_code = status_code

    # Unusual to perform this last, but we need status_code set correctly before calling it
    super().__init__(text=self.model.model_dump_json(), content_type='application/json')


ErrorModelType = TypeVar('ErrorModelType', bound=ErrorModel)


class ErrorModelException[ErrorModelType](HTTPError):
  """
  Pydantic models can't be used in mixin-inheritance so instead if we want to
  raise a model as an exception we have to store it inside a real exception.

  To help the type hinting work this is a generic class parameterized over
  your derived error type.
  """

  status_code: int = 400

  def __init__(self, model: ErrorModelType):
    self.model: ErrorModel = model  # type: ignore | this is at the limits of python's type checker
    self.status_code = self.model.status_code
    if not self.model.request_id:
      req = get_request()
      self.model.request_id = get_request_id(req) if req else None

    # Unusual to perform this last, but we need status_code set correctly before calling it
    super().__init__(text=self.model.model_dump_json(), content_type='application/json')


class PydanticErrorDetails(BaseModel):
  """
  How a pydantic validation error is represented to the UI
  """

  type: str
  loc: List[int | str]
  msg: str
  input: str
  ctx: Optional[Dict[str, str]] = None


class PydanticValidationError(ErrorModel):
  """
  How a pydantic validation error is represented to the UI
  """

  error: Annotated[str, TSEnum('ErrorCode', 'PydanticValidationError')] = 'PydanticValidationError'
  errors: List[PydanticErrorDetails]


def fix_loc_list(loc: Tuple[int | str, ...]) -> List[int | str]:
  return [x if isinstance(x, int) or isinstance(x, str) else str(x) for x in loc]
