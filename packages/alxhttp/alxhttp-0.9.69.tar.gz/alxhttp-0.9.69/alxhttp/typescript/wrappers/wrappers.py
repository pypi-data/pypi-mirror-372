import sys
from typing import List, TextIO

import humps

from alxhttp.pydantic.basemodel import ErrorModel, PydanticValidationError
from alxhttp.pydantic.route import BaseRouteDetails, ErrorType, RouteDetails
from alxhttp.pydantic.ws_route import WSRouteDetails
from alxhttp.typescript.basic_syntax import braces, enlist, join, jsdoc, obj_init, parens, upper_first
from alxhttp.typescript.syntax_tree import Arg, Destructure, Func, RawStmt, Statement
from alxhttp.typescript.type_index import TypeIndex, extract_class, jsdoc_of_toplevel_fields, nullable_union_of_toplevel_fields, pytype_to_tstype


def gen_usequery_wrapper(rd: RouteDetails[ErrorType], argtype_fields: List[str], response_type_name: str, out: TextIO = sys.stdout):
  usequery_func_name = 'use' + humps.pascalize(rd.ts_name)
  stmts: List[Statement] = [Destructure('args as ArgType', argtype_fields)]
  stmts += [
    RawStmt(
      'return useQuery'
      + parens(
        obj_init(
          [
            ('queryKey', enlist([f"'{usequery_func_name}'"] + argtype_fields)),
            ('staleTime', '5 * 1000'),
            (
              'queryFn',
              'async () => '
              + braces(
                # [f'assertVal({x})' for x in argtype_fields] + # TODO: add this back in with a check on the nullability of the arg
                [f'return await {rd.ts_name}({{ {join(argtype_fields, sep=", ")} }})']
              ),
            ),
            ('enabled', 'enabled'),
            ('placeholderData', 'keepPreviousData'),
          ]
        )
      )
    ),
  ]

  use_query_func = Func(
    name=usequery_func_name,
    is_async=False,
    is_export=True,
    return_decl=f'UseQueryResult<{response_type_name}, ResponseErrors>',
    arguments=[Arg('args', 'HookArgs'), Arg('enabled', 'boolean', default_value='true')],
    statements=stmts,
  )

  out.write(
    jsdoc(
      [
        'A hook that wraps the fetch call using react-query.',
        'args are all nullable so this can be chained with the output of a previous hook easily.',
        f'url: {rd.name}',
        jsdoc_of_toplevel_fields([rd.body, rd.match_info]),
        f'@returns {{{response_type_name}}}',
      ]
    )
  )
  out.write(str(use_query_func))


def gen_mutation_wrapper(rd: RouteDetails[ErrorType], argtype_fields: List[str], response_type_name: str, out: TextIO = sys.stdout):
  hook_arg_checks = braces(
    [f'assertVal({x})' for x in argtype_fields]
    + [
      'assertVals(invalidateQueryKey)',
      f'return await {rd.ts_name}({{ {join(argtype_fields, sep=", ")} }})',
    ]
  )

  query_mutation = Func(
    name=f'use{upper_first(rd.ts_name)}Mutation',
    is_async=False,
    is_export=True,
    return_decl=f'UseMutationResult<{response_type_name}, ResponseErrors, void, unknown>',
    arguments=[Arg('args', 'HookArgs'), Arg('invalidateQueryKey', 'QueryKey')],
    statements=[
      Destructure('args', argtype_fields),
      RawStmt('const queryClient = useQueryClient()'),
      RawStmt(f"""return useMutation({{
    mutationFn: async () => {hook_arg_checks},
    onSuccess: () => {{
      queryClient.invalidateQueries({{ queryKey: invalidateQueryKey }})
    }},
  }})"""),
    ],
  )

  out.write(
    jsdoc(
      [
        'A hook that wraps the fetch call using a react-query mutation',
        'args are all nullable so this can be chained with the output of a previous hook easily.',
        f'url: {rd.name}',
        jsdoc_of_toplevel_fields([rd.body, rd.match_info]),
        f'@return {{{response_type_name}}} return',
      ]
    )
  )
  out.write(str(query_mutation))


def gen_reader_imports(out: TextIO):
  out.write(file_header())
  out.write("import { ClientLoaderFunctionArgs } from '@remix-run/react'\n")
  out.write("import { useQuery, UseQueryResult, keepPreviousData } from '@tanstack/react-query'\n\n")
  out.write(shared_defs())


def gen_writer_imports(out: TextIO):
  out.write(file_header())
  out.write("import { ClientActionFunctionArgs } from '@remix-run/react'\n\n")
  out.write("import { useMutation, UseMutationResult, useQuery, UseQueryResult, useQueryClient, keepPreviousData } from '@tanstack/react-query'\n")
  out.write(shared_defs())


def gen_unions(rd: BaseRouteDetails, ti: TypeIndex, out: TextIO):
  for tu in ti.py_to_ts_union.values():
    out.write(str(tu))


def gen_enums(rd: BaseRouteDetails, ti: TypeIndex, out: TextIO):
  error_types = rd.errors + [ErrorModel, PydanticValidationError]
  for e in error_types:
    ti.recurse_model(e, init_from_wire=True, init_to_wire=False)
  ti.enum_refs['ErrorCode'].add('RequestError')

  out.write(ti.gen_enum_defs())

  out.write(
    jsdoc(
      [
        'The union of all error types that the request could throw.',
        f'url: {rd.name}',
      ]
    )
  )
  out.write(f'export type ResponseErrors = ErrorModel | {join([extract_class(e) for e in error_types], sep="|")};\n\n')

  out.write(jsdoc(['When all else fails this error is thrown']))
  out.write('const RequestError = { error: ErrorCode.RequestError, status_code: -1, request_id: null};\n\n')


def gen_arg_types(rd: RouteDetails, ti: TypeIndex, out: TextIO):
  out.write(f'type ArgType = {pytype_to_tstype(rd.match_info)} & {pytype_to_tstype(rd.body)};\n\n')

  x = nullable_union_of_toplevel_fields('HookArgs', [rd.match_info, rd.body])
  out.write(str(x))


def gen_py_to_wire_funcs(ti: TypeIndex, out: TextIO):
  for wf in ti.py_to_wire_func.values():
    out.write(wf + '\n')


def gen_serialize_wire_funcs(ti: TypeIndex, out: TextIO):
  for wf in ti.serialize_wire_func.values():
    out.write(wf + '\n')


def setup_typeindex(rd: RouteDetails[ErrorType], out: TextIO = sys.stdout) -> TypeIndex:
  ti = TypeIndex()
  ti.recurse_model(rd.match_info, init_from_wire=False, init_to_wire=False)
  ti.recurse_model(rd.body, init_from_wire=False, init_to_wire=True)
  ti.recurse_model(rd.response, init_from_wire=True, init_to_wire=False)

  gen_enums(rd, ti, out)

  for v in ti.py_to_ts.values():
    out.write(str(v))

  gen_unions(rd, ti, out)

  gen_arg_types(rd, ti, out)
  gen_py_to_wire_funcs(ti, out)
  return ti


def setup_ws_typeindex(rd: WSRouteDetails[ErrorType], out: TextIO = sys.stdout) -> TypeIndex:
  ti = TypeIndex()
  ti.recurse_model(rd.match_info, init_from_wire=False, init_to_wire=False)
  ti.recurse_model(rd.client_msg, init_from_wire=False, init_to_wire=True)
  ti.recurse_model(rd.server_msg, init_from_wire=True, init_to_wire=False)

  gen_enums(rd, ti, out)

  for v in ti.py_to_ts.values():
    out.write(str(v))

  gen_unions(rd, ti, out)

  gen_py_to_wire_funcs(ti, out)
  return ti


def file_header() -> str:
  return """/* eslint-disable @typescript-eslint/no-explicit-any */
/*
AUTOGENERATED: do not edit by hand, your changes will be overwritten 
*/
"""


def shared_defs() -> str:
  return """function assertVal<T>(val: T): asserts val is NonNullable<T> {
  if (val === undefined || val === null) {
    throw new Error(`Expected 'val' to be defined, but received ${val}`)
  }
}

export function assertVals<T>(arr: (T | null | undefined)[]): asserts arr is NonNullable<T>[] {
  arr.forEach((val, index) => {
    if (val === undefined || val === null) {
      throw new Error(`Expected element at index ${index} to be defined, but received ${val}`)
    }
  })
}

function unreachable(): never {
  throw new Error(`unreachable code reached`)
}

type QueryKey = (string | number | null | undefined)[]
\n\n"""
