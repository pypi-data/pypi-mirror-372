from concurrent.futures import Executor
from typing import Optional, TypeVar

import pydantic
from aiohttp import web
from aiohttp.typedefs import LooseHeaders

from alxhttp.pydantic.basemodel import Empty

ResponseType = TypeVar('ResponseType', bound=pydantic.BaseModel)


class Response[ResponseType](web.Response):
  def __init__(
    self,
    *,
    body: ResponseType,
    status: int = 200,
    reason: Optional[str] = None,
    headers: Optional[LooseHeaders] = None,
    content_type: Optional[str] = 'application/json',
    charset: Optional[str] = None,
    zlib_executor_size: Optional[int] = None,
    zlib_executor: Optional[Executor] = None,
  ):
    super().__init__(
      body=None,
      status=status,
      reason=reason,
      text=body.model_dump_json(),  # type: ignore
      headers=headers,
      content_type=content_type,
      charset=charset,
      zlib_executor_size=zlib_executor_size,
      zlib_executor=zlib_executor,
    )


class EmptyResponse(Response[Empty]):
  def __init__(self):
    super().__init__(body=Empty())
