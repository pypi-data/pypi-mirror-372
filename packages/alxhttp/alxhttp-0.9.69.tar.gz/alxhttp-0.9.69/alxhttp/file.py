from aiohttp.typedefs import Handler, PathLike
from aiohttp.web import FileResponse


def get_file(path: PathLike) -> Handler:
  async def handler(_):
    return FileResponse(path)

  return handler
