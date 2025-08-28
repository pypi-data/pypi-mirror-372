import pydantic
from aiohttp.typedefs import Handler
from aiohttp.web import Request, StreamResponse, middleware

from alxhttp.pydantic.basemodel import PydanticErrorDetails, PydanticValidationError, fix_loc_list


@middleware
async def pydantic_validation(request: Request, handler: Handler) -> StreamResponse:
  """
  Ensure that any Pydantic validation exceptions become JSON
  responses.
  """
  try:
    return await handler(request)
  except pydantic.ValidationError as ve:
    raise PydanticValidationError(
      errors=[PydanticErrorDetails(type=x['type'], loc=fix_loc_list(x['loc']), msg=x['msg'], input=str(x['input']), ctx=x.get('ctx')) for x in ve.errors(include_url=False)]
    ).exception() from ve
