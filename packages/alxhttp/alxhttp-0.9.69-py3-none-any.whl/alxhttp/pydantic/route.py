from dataclasses import dataclass
from functools import partial
from typing import Any, Awaitable, Callable, List, Optional, Type, TypeVar

import humps
from aiohttp import web
from aiohttp.web_request import Request as WebRequest
from aiohttp.web_response import StreamResponse
from aiohttp.web_urldispatcher import UrlDispatcher

from alxhttp.pydantic.basemodel import Empty, ErrorModel
from alxhttp.pydantic.request import BodyType, MatchInfoType, QueryType, Request
from alxhttp.pydantic.response import Response, ResponseType
from alxhttp.server import ServerType

ErrorType = TypeVar('ErrorType', bound=ErrorModel)


@dataclass
class BaseRouteDetails[ErrorType]:
  name: str
  match_info: Type
  query: Type
  ts_name: str
  errors: List[Type[ErrorType]]


@dataclass
class RouteDetails[ErrorType](BaseRouteDetails[ErrorType]):
  verb: str
  body: Type
  response: Type


def get_route_details(func: Callable) -> RouteDetails:
  return RouteDetails(
    name=func._alxhttp_route_name,
    verb=func._alxhttp_route_verb,
    match_info=func._alxhttp_match_info,
    response=func._alxhttp_response,
    body=func._alxhttp_body,
    query=func._alxhttp_query,
    ts_name=func._alxhttp_ts_name,
    errors=func._alxhttp_errors or [],
  )


def route(
  verb: str,
  name: str,
  ts_name: str | None = None,
  match_info: Type[MatchInfoType] = Empty,
  body: Type[BodyType] = Empty,
  query: Type[QueryType] = Empty,
  response: Type[ResponseType] = Empty,
  errors: Optional[List[Type[ErrorType]]] = None,
):
  def decorator(
    func: Callable[
      [ServerType, Request[match_info, body, query]],
      Awaitable[Response[response]],
    ],
  ):
    new_ts_name = ts_name
    if not new_ts_name:
      new_ts_name = humps.camelize(func.__name__)

    async def wrapper(server: ServerType, request: web.Request, *args: Any, **kwargs: Any) -> Response[ResponseType]:
      vr = await Request[match_info, body, query].from_request(request)
      return await func(server, vr, *args, **kwargs)

    assert name == name.strip()

    setattr(wrapper, '_alxhttp_route_name', name)
    setattr(wrapper, '_alxhttp_route_verb', verb)
    setattr(wrapper, '_alxhttp_match_info', match_info)
    setattr(wrapper, '_alxhttp_response', response)
    setattr(wrapper, '_alxhttp_body', body)
    setattr(wrapper, '_alxhttp_query', query)
    setattr(wrapper, '_alxhttp_ts_name', new_ts_name)
    setattr(wrapper, '_alxhttp_errors', errors)
    return wrapper

  return decorator


def add_route(
  server: ServerType,
  router: UrlDispatcher,
  route_handler: Callable[[ServerType, WebRequest], Awaitable[StreamResponse]],
) -> None:
  route_details = get_route_details(route_handler)
  handler = partial(route_handler, server)
  router.add_route(route_details.verb, route_details.name, handler)
  print(f'- {route_details.verb} {route_details.name}')
