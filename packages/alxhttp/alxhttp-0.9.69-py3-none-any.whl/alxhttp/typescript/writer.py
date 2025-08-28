import pathlib
import subprocess
from typing import List, Sequence

import humps

from alxhttp.pydantic.route import RouteDetails, get_route_details
from alxhttp.pydantic.ws_route import WSRouteDetails, get_ws_route_details
from alxhttp.server import ServerHandler
from alxhttp.typescript.wrappers.gen_delete_wrapper import generate_delete_api_wrapper
from alxhttp.typescript.wrappers.gen_get_wrapper import generate_get_api_wrapper
from alxhttp.typescript.wrappers.gen_post_wrapper import generate_post_api_wrapper
from alxhttp.typescript.wrappers.gen_ws_wrapper import generate_ws_api_wrapper


def gen_ts_for_route(route_details: RouteDetails, base_path: str = '.', base_url: str = 'http://127.0.0.1:8081/', pretty: bool = False, generated_files: set | None = None) -> None:
  root = pathlib.Path(base_path)
  if not root.exists():
    root.mkdir()
  ts_file = root / f'{humps.decamelize(route_details.ts_name)}.ts'

  if generated_files is not None:
    if ts_file in generated_files:
      raise ValueError('already generated!')
    generated_files.add(ts_file)

  print(f'regenerating: {ts_file}')
  with open(ts_file, 'w') as f:
    if route_details.verb == 'GET':
      generate_get_api_wrapper(route_details, out=f, base_url=base_url)
    elif route_details.verb == 'POST':
      generate_post_api_wrapper(route_details, out=f, base_url=base_url)
    elif route_details.verb == 'DELETE':
      generate_delete_api_wrapper(route_details, out=f, base_url=base_url)
    else:
      assert False
    f.flush()
  if pretty:
    run_prettier(ts_file)


def gen_ts_for_routes(
  routes: Sequence[ServerHandler],
  base_path: str = 'ts',
  base_url: str = 'http://127.0.0.1:8081/',
) -> None:
  generated_files = set()
  for route_handler in routes:
    route_details = get_route_details(route_handler)
    gen_ts_for_route(route_details, base_path=base_path, base_url=base_url, generated_files=generated_files)
  run_prettier(pathlib.Path(base_path))


def gen_ts_for_ws_route(route_details: WSRouteDetails, base_path: str = '.', base_url: str = 'http://127.0.0.1:8081/', pretty: bool = False, generated_files: set | None = None) -> None:
  root = pathlib.Path(base_path)
  if not root.exists():
    root.mkdir()
  ts_file = root / f'{humps.decamelize(route_details.ts_name)}.ts'

  if generated_files is not None:
    if ts_file in generated_files:
      raise ValueError('already generated!')
    generated_files.add(ts_file)

  print(f'regenerating: {ts_file}')
  with open(ts_file, 'w') as f:
    generate_ws_api_wrapper(route_details, out=f, base_url=base_url)
    f.flush()
  if pretty:
    run_prettier(ts_file)


def gen_ts_for_ws_routes(
  routes: Sequence[ServerHandler],
  base_path: str = 'ts',
  base_url: str = 'http://127.0.0.1:8081/',
) -> None:
  generated_files = set()
  for route_handler in routes:
    route_details = get_ws_route_details(route_handler)
    gen_ts_for_ws_route(route_details, base_path=base_path, base_url=base_url, generated_files=generated_files)
  run_prettier(pathlib.Path(base_path))


def run_prettier(path: pathlib.Path, should_raise: bool = True, opts: List[str] | None = None) -> None:
  if not opts:
    opts = []

  try:
    # Construct the command
    command = ['bun', 'x', 'prettier', '--ignore-path', '/dev/null', '-w', str(path)] + opts

    # Run the command
    r = subprocess.run(command, check=True, capture_output=True, text=True)
    print(f'Output: {" ".join(command)}')
    print(f'Output: {r.stderr}')
    print(f'Output: {r.stdout}')

  except subprocess.CalledProcessError as e:
    print(f'Error running prettier: {e}')
    print(f'Output: {e.output}')
    print(f'Error output: {e.stderr}')
    if should_raise:
      raise e
