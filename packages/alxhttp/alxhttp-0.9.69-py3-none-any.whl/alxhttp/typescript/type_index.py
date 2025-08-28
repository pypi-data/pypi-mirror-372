import typing
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, List, Set, get_type_hints

from pydantic import BaseModel, HttpUrl

from alxhttp.pydantic.route import RouteDetails
from alxhttp.typescript.basic_syntax import braces
from alxhttp.typescript.syntax_tree import ObjectInit, ObjectInitField, ObjectType, ObjectTypeField, TypeDecl, UnionType
from alxhttp.typescript.type_checks import (
  extract_class,
  get_literal,
  is_alias,
  is_annotated,
  is_dict,
  is_generic_type,
  is_list,
  is_literal,
  is_model_type,
  is_optional,
  is_safe_primitive_type_or_union,
  is_tuple,
  is_type_or_annotated_type,
  is_union,
  is_union_of_models,
  is_union_of_safe_primitive_types_or_none,
)
from alxhttp.typescript.type_conversion import pytype_to_tstype
from alxhttp.typescript.types import SAFE_PRIMITIVE_TYPES, TSEnum, TSUndefined


class PydanticError(BaseModel):
  type: str
  loc: List[str]
  msg: str
  input: str
  ctx: Dict[str, str]


class PydanticErrorResp(BaseModel):
  errors: List[PydanticError]


def model_to_type(name: str, model) -> ObjectType:
  model_fields = get_type_hints(model, include_extras=True)
  fields = []
  for field_name, field_type in model_fields.items():
    fields.append(ObjectTypeField(field_name, TypeDecl(field_type), None))

  return ObjectType(name, fields)


def nullable_union_of_toplevel_fields(name: str, models) -> ObjectType:
  fields: List[ObjectTypeField] = []
  for model in models:
    model_fields = get_type_hints(model, include_extras=True)

    for field_name, field_type in model_fields.items():
      if not is_optional(field_type):
        field_type = field_type | None | TSUndefined
      fields.append(ObjectTypeField(field_name, TypeDecl(field_type), None))

  return ObjectType(name, fields, export=False)


def jsdoc_of_toplevel_fields(models) -> List[str]:
  fields: List[ObjectTypeField] = []
  for model in models:
    model_fields = get_type_hints(model, include_extras=True)

    for field_name, field_type in model_fields.items():
      fields.append(ObjectTypeField(field_name, TypeDecl(field_type), None))

  return [f'@param {{{f.decl}}} {f.name}' for f in fields]


def extract_enum_references(enum: Dict[str, Set[str]], model) -> None:
  model_fields = get_type_hints(model, include_extras=True)
  for _, field_type in model_fields.items():
    if is_annotated(field_type):
      targs = typing.get_args(field_type)
      if isinstance(targs[1], TSEnum):
        enum[targs[1].name].add(targs[1].value)


def gen_wire_func(name: str, ret_type: str, object_init: ObjectInit):
  return f'export function {name}(root: any): {ret_type} {{ return {object_init} }};\n'


def recurse_model_types(t: type, seen: Set[type] | None = None) -> Generator[type, None, None]:
  if seen is None:
    seen = set()

  if t in seen:
    return
  seen.add(t)

  if is_alias(t):
    if is_union_of_models(t.__value__):
      yield t
    yield from recurse_model_types(t.__value__, seen)

  if is_generic_type(t):
    for arg in typing.get_args(t):
      yield from recurse_model_types(arg, seen)
  elif is_model_type(t):
    yield t

    model_fields = get_type_hints(t)
    for _, field_type in model_fields.items():
      yield from recurse_model_types(field_type, seen)


def _discrimination_expr(src_name, type_args) -> str:
  discrimination_expr = ''
  first_first_name = None
  finished = False
  for n, subtype in enumerate(type_args):
    first_name, first_field_type = list(get_type_hints(subtype).items())[0]
    if not first_first_name:
      first_first_name = first_name
    assert first_name == first_first_name  # simplifying assumption: all subtypes will have a common first literal key
    if is_literal(first_field_type):
      literal_value = get_literal(first_field_type)
      if isinstance(literal_value, str):
        literal_value = f"'{literal_value}'"

      discrimination_expr += f'({src_name}.{first_name} === {literal_value}) ? get{pytype_to_tstype(subtype)}FromWire({src_name}) : '
    elif n == len(type_args) - 1:
      finished = True
      discrimination_expr += f'get{pytype_to_tstype(subtype)}FromWire({src_name})'

  if not finished:
    discrimination_expr += ' unreachable()'
  return discrimination_expr


@dataclass
class TypeIndex:
  py_to_ts: Dict[type, ObjectType] = field(default_factory=dict)
  ts_to_py: Dict[str, type] = field(default_factory=dict)

  py_to_wire_func: Dict[type, str] = field(default_factory=dict)
  py_to_wire_func_name: Dict[type, str] = field(default_factory=dict)

  serialize_wire_func: Dict[type, str] = field(default_factory=dict)
  serialize_wire_func_name: Dict[type, str] = field(default_factory=dict)

  py_to_ts_union: Dict[type, UnionType] = field(default_factory=dict)

  enum_refs = defaultdict(set)

  def gen_enum_defs(self) -> str:
    tdefs = []
    for ename, evals in self.enum_refs.items():
      tdefs.append(f'enum {ename} {braces([f"{ev} = '{ev}'" for ev in sorted(evals)], sep=",")};')
    return '\n\n'.join(tdefs) + '\n\n'

  def body_and_match_field_names(self, rd: RouteDetails) -> List[str]:
    body_arg_names = [x.name for x in self.py_to_ts[rd.body].fields]
    match_info_arg_names = [x.name for x in self.py_to_ts[rd.match_info].fields]
    return match_info_arg_names + body_arg_names

  def recurse_model(self, mt: type, init_from_wire: bool = True, init_to_wire: bool = True) -> None:
    for m in recurse_model_types(mt):
      if is_alias(m) and is_union_of_models(m.__value__):
        type_name = str(m)
        union_type = m.__value__
        self.py_to_ts_union[union_type] = UnionType(type_name, members=[extract_class(c) for c in typing.get_args(union_type)], export=True)
        if init_from_wire:
          self.init_discriminated_union_from_wire(union_type)
      else:
        ts_name = extract_class(m)
        t = model_to_type(ts_name, m)
        extract_enum_references(self.enum_refs, m)
        self.py_to_ts[m] = t
        self.ts_to_py[ts_name] = m

        if init_from_wire:
          self.init_from_wire(m)
        if init_to_wire:
          self.init_to_wire(m)

  def _gen_init_field_assignment(self, type: type, src_name: str = 'root', depth: int = 0) -> str:
    depth += 1

    kn = f'k{depth}'
    vn = f'v{depth}'

    type_args = typing.get_args(type)

    if type in SAFE_PRIMITIVE_TYPES:
      return src_name
    elif type == HttpUrl:
      return src_name
    elif is_literal(type):
      return src_name
    elif type == datetime:
      return f'new Date({src_name} * 1000)'
    elif type == Any:
      return src_name
    elif is_annotated(type):
      return self._gen_init_field_assignment(type_args[0], src_name, depth)
    elif is_alias(type):
      return self._gen_init_field_assignment(type.__value__, src_name, depth)
    elif is_list(type) or is_tuple(type):
      if is_safe_primitive_type_or_union(type_args[0]):
        # Small optimization
        return src_name

      return f'{src_name}.map(({vn}: {pytype_to_tstype(type_args[0])}) => {{ return {self._gen_init_field_assignment(type_args[0], vn, depth)} }})'
    elif is_union_of_safe_primitive_types_or_none(type):
      return src_name
    elif is_optional(type):
      return f'({src_name} === null) ? null : ' + self._gen_init_field_assignment(type_args[0], src_name, depth)
    elif is_union_of_models(type):
      return _discrimination_expr(src_name, type_args)
    elif is_union(type):
      # This case represents a complex union i.e "str | datetime"
      assert False
    elif is_dict(type):
      assert is_type_or_annotated_type(type_args[0], str)
      ktype = pytype_to_tstype(type_args[0])
      vtype = pytype_to_tstype(type_args[1])
      return f'Object.fromEntries(Object.entries({src_name} as Record<{ktype}, {vtype}>).map(([{kn}, {vn}]) => {{ return [{kn}, {self._gen_init_field_assignment(type_args[1], vn, depth)}] }} ))'
    elif is_model_type(type):
      return f'get{pytype_to_tstype(type)}FromWire({src_name})'
    else:
      raise ValueError

  def _gen_uninit_field_assignment(self, type: type, src_name: str = 'root', depth: int = 0) -> str:
    depth += 1

    kn = f'k{depth}'
    vn = f'v{depth}'

    type_args = typing.get_args(type)

    if type in SAFE_PRIMITIVE_TYPES:
      return src_name
    elif is_literal(type):
      return src_name
    elif type == datetime:
      return f'{src_name}.getTime()'
    elif type == Any:
      return src_name
    elif is_annotated(type):
      return self._gen_uninit_field_assignment(type_args[0], src_name, depth)
    elif is_alias(type):
      return self._gen_uninit_field_assignment(type.__value__, src_name, depth)
    elif is_list(type) or is_tuple(type):
      # TODO: ignoring tuple types
      return f'{src_name}.map(({vn}: {pytype_to_tstype(type_args[0])}) => {{ return {self._gen_uninit_field_assignment(type_args[0], vn, depth)} }})'
    elif is_union_of_safe_primitive_types_or_none(type):
      return src_name
    elif is_optional(type):
      return f'({src_name} === null) ? null : ' + self._gen_uninit_field_assignment(type_args[0], src_name, depth)
    elif is_union_of_models(type):
      discrimination_expr = ''
      first_first_name = None
      finished = False
      for n, subtype in enumerate(type_args):
        first_name, first_field_type = list(get_type_hints(subtype).items())[0]
        if not first_first_name:
          first_first_name = first_name
        assert first_name == first_first_name  # simplifying assumption: all subtypes will have a common first literal key
        if is_literal(first_field_type):
          literal_value = get_literal(first_field_type)
          if isinstance(literal_value, str):
            literal_value = f"'{literal_value}'"

          discrimination_expr += f'({src_name}.{first_name} === {literal_value}) ? convert{pytype_to_tstype(subtype)}ToWire({src_name}) : '
        elif n == len(type_args) - 1:
          finished = True
          discrimination_expr += f'convert{pytype_to_tstype(subtype)}ToWire({src_name})'

      if not finished:
        discrimination_expr += ' unreachable()'
      return discrimination_expr
    elif is_union(type):
      # This case represents a complex union i.e "str | datetime"
      assert False
    elif is_dict(type):
      assert is_type_or_annotated_type(type_args[0], str)
      ktype = pytype_to_tstype(type_args[0])
      vtype = pytype_to_tstype(type_args[1])
      return f'Object.fromEntries(Object.entries({src_name} as Record<{ktype}, {vtype}>).map(([{kn}, {vn}]) => {{ return [{kn}, {self._gen_uninit_field_assignment(type_args[1], vn, depth)}] }} ))'

    elif is_model_type(type):
      return f'convert{pytype_to_tstype(type)}ToWire({src_name})'
    else:
      raise ValueError

  def init_discriminated_union_from_wire(self, py_type: type, wire_arg: str = 'root') -> str:
    ts_type = self.py_to_ts_union[py_type]
    de = _discrimination_expr(wire_arg, typing.get_args(py_type))

    wire_func_name = f'get{ts_type.name}FromWire'
    wire_func = f'export function {wire_func_name}(root: any): {ts_type.name} {{ return {de} }};\n'

    self.py_to_wire_func_name[py_type] = wire_func_name
    self.py_to_wire_func[py_type] = wire_func

    return wire_func

  def init_from_wire(self, py_type: type, wire_arg: str = 'root') -> str:
    """
    Inits a new JS object based on one that came via json over the wire. Allows
    us to do things like turn float timestamps into js Date objects.
    """
    ts_type = self.py_to_ts[py_type]
    field_assignments: List[ObjectInitField] = []
    for tsfield in ts_type.fields:
      field_assignments.append(
        ObjectInitField(
          tsfield.name,
          self._gen_init_field_assignment(tsfield.decl.decl, f'{wire_arg}.{tsfield.name}'),
        )
      )

    object_init = ObjectInit(field_assignments)
    wire_func_name = f'get{ts_type.name}FromWire'
    wire_func = gen_wire_func(wire_func_name, ts_type.name, object_init)

    self.py_to_wire_func_name[py_type] = wire_func_name
    self.py_to_wire_func[py_type] = wire_func

    return wire_func

  def init_to_wire(self, py_type: type, wire_arg: str = 'root') -> str:
    """
    Inits a new JS object to be sent over the wire. Allows
    us to do things like turn js Date objects into float timestamps.
    """
    ts_type = self.py_to_ts[py_type]
    field_assignments: List[ObjectInitField] = []
    for tsfield in ts_type.fields:
      field_assignments.append(
        ObjectInitField(
          tsfield.name,
          self._gen_uninit_field_assignment(tsfield.decl.decl, f'{wire_arg}.{tsfield.name}'),
        )
      )

    object_init = ObjectInit(field_assignments)
    wire_func_name = f'convert{ts_type.name}ToWire'
    wire_func = gen_wire_func(wire_func_name, ts_type.name, object_init)

    self.serialize_wire_func_name[py_type] = wire_func_name
    self.serialize_wire_func[py_type] = wire_func

    return wire_func
