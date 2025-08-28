import types

SAFE_PRIMITIVE_TYPES = {str, int, float, bool}

SAFE_PRIMITIVE_TYPES_OR_NONE = SAFE_PRIMITIVE_TYPES | {types.NoneType}


class TSRaw:
  def __init__(self, value):
    self.value = value


class TSEnum:
  def __init__(self, name: str, value: str):
    self.name = name
    self.value = value


class TSUndefined:
  pass
