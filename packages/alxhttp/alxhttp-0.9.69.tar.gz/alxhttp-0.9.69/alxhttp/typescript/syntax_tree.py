from dataclasses import dataclass, field
from typing import List, Tuple

from alxhttp.typescript.basic_syntax import braces, join, space
from alxhttp.typescript.type_conversion import pytype_to_tstype


@dataclass
class Arg:
  name: str
  type_decl: str | type
  default_value: str | None = field(default=None)

  def __str__(self) -> str:
    if isinstance(self.type_decl, str):
      type_decl = self.type_decl
    else:
      type_decl = pytype_to_tstype(self.type_decl)
    default_decl = ''
    if self.default_value:
      default_decl = f' = {self.default_value}'
    return f'{self.name}: {type_decl}{default_decl}'


@dataclass
class Statement:
  pass


@dataclass
class Destructure(Statement):
  name: str
  arguments: List[str]

  def __str__(self) -> str:
    return space(f'const {{ {join(self.arguments, sep=", ")} }} = {self.name};')


@dataclass
class ReturnFuncCall(Statement):
  name: str
  arguments: List[str]
  is_async: bool = field(default=True)

  def __str__(self) -> str:
    await_expr = 'await ' if self.is_async else ''
    return space(f'return {await_expr}{self.name}({{ {join(self.arguments, sep=", ")} }});')


@dataclass
class If(Statement):
  cond: str
  stmts: List[Statement]

  def __str__(self) -> str:
    return space(f'if ({self.cond}) {{ {join(self.stmts)} }}')


@dataclass
class SwitchStmt(Statement):
  cond: str
  case_stmts: List[Tuple[str, Statement]]
  default_stmt: Statement

  def __str__(self) -> str:
    cases = join([f'case {cond}: {{ {stmt} }}' for cond, stmt in self.case_stmts] + [f'default: {{ {self.default_stmt} }}'])

    return space(f'switch ({self.cond}) {{ {cases} }}')


@dataclass
class TryCatch(Statement):
  try_stmts: List[Statement]
  catch_stmts: List[Statement]

  def __str__(self) -> str:
    return space(f'try {{ {join(self.try_stmts)} }} catch(error: any) {{ {join(self.catch_stmts)} }}')


@dataclass
class AnonFuncCall(Statement):
  statements: List[str]

  def __str__(self) -> str:
    return space(f'() => {{ }} {{ {join(self.statements, sep="\n")} }}')


@dataclass
class CheckedParamsAccess(Statement):
  name: str

  def __str__(self) -> str:
    return space(f"""const {self.name} = params.{self.name};
                 if (!{self.name}) {{ throw Error('failed to access param'); }}
""")


@dataclass
class CheckedFormAccess(Statement):
  name: str

  def __str__(self) -> str:
    return space(f"""const {self.name} = formData.get('{self.name}')?.toString();
                 if (!{self.name}) {{ throw Error('failed to access form data'); }}
""")


@dataclass
class Func:
  name: str
  return_decl: str
  arguments: List[Arg]
  statements: List[Statement]
  is_async: bool = field(default=True)
  is_export: bool = field(default=False)

  def __str__(self) -> str:
    export = 'export ' if self.is_export else ''
    prefix = 'async ' if self.is_async else ''
    return f"""{export} {prefix} function {self.name}({join(self.arguments, sep=', ')}): {self.return_decl}
    {braces(self.statements)}\n\n"""


@dataclass
class RawStmt(Statement):
  stmt: str

  def __str__(self) -> str:
    return self.stmt


@dataclass
class JsonPost(Statement):
  url: str
  args: str
  response_type: str

  def __str__(self) -> str:
    return f"""
    const response = await postJSON(`{self.url}`, {self.args});
    
    if (response.status == 200 && response.body) {{
        return [get{self.response_type}FromWire(response.body), response];
    }}
    // throw new Error(`POST failed: ${{response.status}} ${{response.text}}`);
    return [null, response];
    
    """


@dataclass
class JsonGet(Statement):
  url: str
  response_type: str

  def __str__(self) -> str:
    return f"""
    const response = await getJSON(`{self.url}`);
    
    if (response.status == 200 && response.body) {{
        return [get{self.response_type}FromWire(response.body), response];
    }}
    // throw new Error(`GET failed: ${{response.status}} ${{response.text}}`);
    return [null, response];
    
    """


@dataclass
class TypeDecl:
  decl: type

  def __str__(self) -> str:
    if isinstance(self.decl, str):
      raise ValueError
    return pytype_to_tstype(self.decl)


@dataclass
class ObjectTypeField:
  name: str
  decl: TypeDecl
  default_value: str | None

  def __str__(self) -> str:
    default_value = f' = {self.default_value}' if self.default_value else ''
    return f'{self.name}: {self.decl}{default_value}'


@dataclass
class ObjectType:
  name: str
  fields: List[ObjectTypeField]
  export: bool = True

  def __str__(self) -> str:
    export_decl = 'export ' if self.export else ''
    if not self.fields:
      return f'{export_decl}type {self.name} = Record<string, unknown>\n\n'
    return f'{export_decl}type {self.name} = {braces(self.fields, sep=",\n")}\n\n'


@dataclass
class UnionType:
  name: str
  members: List[str]
  export: bool = True

  def __str__(self) -> str:
    export_decl = 'export ' if self.export else ''
    assert self.members
    return f'{export_decl}type {self.name} = {"|".join(self.members)}\n\n'


@dataclass
class ObjectInitField:
  name: str
  value: str | None

  def __str__(self) -> str:
    return f'{self.name}: {self.value}'


@dataclass
class ObjectInit:
  fields: List[ObjectInitField]

  def __str__(self) -> str:
    return f'{braces(self.fields, sep=",\n")}\n'
