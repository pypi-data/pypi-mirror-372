import json
from typing import Type, TypeVar

import pydantic
from aiohttp import web

from alxhttp.pydantic.basemodel import BaseModel

RequestType = TypeVar('RequestType', bound='Request')
MatchInfoType = TypeVar('MatchInfoType', bound=BaseModel)
BodyType = TypeVar('BodyType', bound=BaseModel)
QueryType = TypeVar('QueryType', bound=BaseModel)


class Request[MatchInfoType, BodyType, QueryType](BaseModel):
  _web_request: web.Request = pydantic.PrivateAttr()
  match_info: MatchInfoType
  body: BodyType
  query: QueryType

  @classmethod
  async def from_request(cls: Type[RequestType], request: web.Request) -> RequestType:
    text = await request.text()
    body = json.loads(text) if text else {}

    m = cls.model_validate(
      {
        'match_info': request.match_info,
        'body': body,
        'query': dict(request.query),
      }
    )
    m._web_request = request
    return m
