import sys
from typing import List, TextIO

from alxhttp.pydantic.route import ErrorType, RouteDetails
from alxhttp.typescript.basic_syntax import drop_leading_slash, jsdoc, python_to_js_string_template
from alxhttp.typescript.syntax_tree import Arg, Destructure, Func, If, RawStmt, SwitchStmt
from alxhttp.typescript.type_index import jsdoc_of_toplevel_fields, pytype_to_tstype
from alxhttp.typescript.wrappers.wrappers import gen_reader_imports, gen_usequery_wrapper, setup_typeindex


def gen_fetch_get_wrapper(rd: RouteDetails, base_url: str, argtype_fields: List[str], response_type_name: str, out: TextIO):
  api_url = f'${{base_url}}{drop_leading_slash(python_to_js_string_template(rd.name))}'

  tf = Func(
    name=rd.ts_name,
    is_export=True,
    return_decl=f'Promise<{response_type_name}>',
    arguments=[Arg('args', 'ArgType'), Arg('base_url', 'string', f"'{base_url}'"), Arg('timeout', 'number', '2000'), Arg('...rest', 'any[]')],
    statements=[
      Destructure('args', argtype_fields),
      RawStmt(f'const url = `{api_url}`;'),
      RawStmt("const response = await fetch(url, { method: 'GET', })"),
      If('response.status == 200', [RawStmt(f'return get{response_type_name}FromWire(await response.json());')]),
      RawStmt('const data = await response.json()'),
      If(
        'data.error',
        [
          SwitchStmt(
            cond='data.error',
            case_stmts=[('ErrorCode.PydanticValidationError', RawStmt('throw getPydanticValidationErrorFromWire(data)'))],
            default_stmt=RawStmt('throw getErrorModelFromWire(data);'),
          ),
        ],
      ),
      RawStmt('throw RequestError;'),
    ],
  )
  out.write(jsdoc(['The main fetch wrapper that handles serialization/deserialization', f'url: {rd.name}', jsdoc_of_toplevel_fields([rd.body, rd.match_info]), f'@returns {{{response_type_name}}}']))
  out.write(str(tf))


def generate_get_api_wrapper(rd: RouteDetails[ErrorType], base_url: str = 'http://127.0.0.1:8081/', out: TextIO = sys.stdout) -> None:
  gen_reader_imports(out)

  ti = setup_typeindex(rd, out)
  argtype_fields = ti.body_and_match_field_names(rd)
  response_type_name = pytype_to_tstype(rd.response)

  gen_fetch_get_wrapper(rd, base_url, argtype_fields, response_type_name, out)
  gen_usequery_wrapper(rd, argtype_fields, response_type_name, out)
