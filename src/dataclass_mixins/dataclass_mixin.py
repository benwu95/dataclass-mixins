import re
import types
from dataclasses import fields, is_dataclass, MISSING
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import get_args, get_origin, get_type_hints, Any, Literal, Self, Union


class _WRONG_VALUE_TYPE:
    pass


WRONG_VALUE = _WRONG_VALUE_TYPE()
BASE_VALUE_TYPES = (str, int, float, bool, datetime, Enum, list, tuple, set)


# copy from dataclasses.py
def _asdict(obj, dict_factory) -> Any:
    if is_dataclass(obj):
        result = []
        for f in fields(obj):
            value = _asdict(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))
        return dict_factory(result)
    if isinstance(obj, tuple) and hasattr(obj, '_fields'):
        return type(obj)(*[_asdict(v, dict_factory) for v in obj])
    if isinstance(obj, (list, tuple)):
        return type(obj)(_asdict(v, dict_factory) for v in obj)
    if isinstance(obj, dict):
        return type(obj)((_asdict(k, dict_factory), _asdict(v, dict_factory)) for k, v in obj.items())
    return obj


def snake_to_camel_case(string: str):
    if len(string) > 1 and re.match(r'^[A-Z]$', string[0]) and re.match(r'^[a-z0-9]$', string[1]):
        string = string[0].lower() + string[1:]
    return re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), string)


def camel_to_snake_case(string: str):
    # return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()
    # NOTE(Ben Wu): want to transform `isABC` into `is_ABC`, instead of `is_a_b_c`
    r = ''
    prev_s = ''
    next_s = ''
    for i, c in enumerate(string):
        next_s = string[i + 1] if i + 1 < len(string) else ''
        if re.match(r'^[a-z0-9]$', prev_s) and re.match(r'^[A-Z]$', c):
            r += '_'
            if re.match(r'^[a-z0-9]?$', next_s):
                r += c.lower()
            else:
                r += c
        elif re.match(r'^[A-Z]$', prev_s) and re.match(r'^[A-Z]$', c) and re.match(r'^[a-z]$', next_s):
            r += f'_{c.lower()}'
        else:
            r += c
        prev_s = c
    if len(r) > 0 and re.match(r'^[A-Z]$', r[0]):
        if len(r) == 1:
            return r.lower()
        if re.match(r'^[A-Z][a-z0-9]', r):
            return r[0].lower() + r[1:]
    return r


def to_data(data) -> Any:
    if isinstance(data, dict):
        return {k: to_data(v) for k, v in data.items()}
    if isinstance(data, (list, tuple, set)):
        return [to_data(d) for d in data]
    if isinstance(data, Enum):
        return data.value
    if isinstance(data, datetime):
        return data.timestamp()
    return data


def to_camel_case_data(data):
    if isinstance(data, dict):
        return {snake_to_camel_case(k): to_camel_case_data(v) for k, v in data.items()}
    if isinstance(data, (list, tuple, set)):
        return [to_camel_case_data(d) for d in data]
    return to_data(data)


def to_snake_case_data(data):
    if isinstance(data, dict):
        return {camel_to_snake_case(k): to_snake_case_data(v) for k, v in data.items()}
    if isinstance(data, (list, tuple, set)):
        return [to_snake_case_data(d) for d in data]
    return to_data(data)


def to_camel_case_json(dc) -> dict:
    return _asdict(dc, dict_factory=lambda f: {snake_to_camel_case(k): to_camel_case_data(v) for k, v in f})


def to_snake_case_json(dc) -> dict:
    return _asdict(dc, dict_factory=lambda f: {camel_to_snake_case(k): to_snake_case_data(v) for k, v in f})


def from_data(t: type, data) -> Any:
    def _create_dataclass(_t: type, _data):
        if isinstance(_data, dict):
            get_field_data = lambda f: _data.get(f.name, MISSING)
        else:
            get_field_data = lambda f: getattr(_data, f.name, MISSING)
        kwargs = {}
        type_hints = get_type_hints(_t)
        for f in fields(_t):
            if f.init:
                raw_value = get_field_data(f)
                value = from_data(type_hints[f.name], raw_value)
                if value is WRONG_VALUE:
                    raise ValueError(f'Invalid value {raw_value} for {f.name} in {_t}')
                if isinstance(value, (list, tuple, set)) and WRONG_VALUE in value:
                    raise ValueError(f'Invalid value {raw_value} for {f.name} in {_t}')
                if isinstance(value, dict) and (WRONG_VALUE in value.keys() or WRONG_VALUE in value.values()):
                    raise ValueError(f'Invalid value {raw_value} for {f.name} in {_t}')
                if raw_value is MISSING:
                    if f.default is not MISSING:
                        value = f.default
                    elif f.default_factory is not MISSING:
                        value = f.default_factory()
                    elif value is MISSING:
                        value = _create_default_data(type_hints[f.name])
                        if value is MISSING:
                            value = None
                kwargs[f.name] = value
        return _t(**kwargs)

    def _create_default_data(_t: type):
        _o = get_origin(_t) or _t
        if _o is list:
            return []
        if _o is set:
            return set()
        if _o is dict:
            return {}
        if is_dataclass(_o):
            return _create_dataclass(_o, None)
        return MISSING

    if t is Any:
        return data if data is not MISSING else None

    origin_type = get_origin(t) or t
    args_types = get_args(t)

    if origin_type in (types.UnionType, Union):
        if data is MISSING:
            if types.NoneType in args_types:
                return None
            return _create_default_data(args_types[0])
        for args_type in args_types:
            try:
                r = from_data(args_type, data)
                if r is not WRONG_VALUE:
                    return r
            except ValueError:
                pass
        return WRONG_VALUE

    if origin_type is Literal:
        for args_type in args_types:
            if isinstance(args_type, Enum) and data == args_type.value:
                return args_type
            if data == args_type:
                return data
            if data is MISSING and args_type is None:
                return None
        return WRONG_VALUE

    if data is MISSING:
        return MISSING

    if origin_type in {list, dict, tuple, set}:
        if origin_type is list:
            if isinstance(data, (list, tuple, set)):
                if len(args_types) == 1:
                    return [from_data(args_types[0], d) for d in data]
                return list(data)
        elif origin_type is dict:
            if isinstance(data, dict):
                if len(args_types) == 2:
                    return {from_data(args_types[0], k): from_data(args_types[1], v) for k, v in data.items()}
                return data
        elif origin_type is tuple:
            if isinstance(data, (list, tuple)):
                if len(args_types) == len(data):
                    return tuple(from_data(args_type, d) for args_type, d in zip(args_types, data))
        elif origin_type is set:
            if isinstance(data, (list, tuple, set)):
                if len(args_types) == 1:
                    return {from_data(args_types[0], d) for d in data}
                return set(data)
    elif is_dataclass(origin_type):
        if isinstance(data, origin_type) and getattr(data, '__dataclass_params__').frozen:
            return data
        if data is not None and not isinstance(data, BASE_VALUE_TYPES):
            return _create_dataclass(origin_type, data)
    elif isinstance(data, origin_type):
        return data
    elif issubclass(origin_type, Enum):
        try:
            return origin_type(data)
        except ValueError:
            return WRONG_VALUE
    elif isinstance(data, Enum) and isinstance(data.value, origin_type):
        return data.value
    elif issubclass(origin_type, datetime) and isinstance(data, (int, float)):
        return origin_type.fromtimestamp(data, tz=timezone.utc)
    elif isinstance(data, datetime):
        if origin_type is int:
            return int(data.timestamp())
        if origin_type is float:
            return data.timestamp()
    elif origin_type is float and isinstance(data, (int, Decimal)):
        return float(data)
    elif origin_type is Decimal and isinstance(data, (int, float)):
        return Decimal(str(data))
    elif origin_type is int and isinstance(data, (float, Decimal)) and data % 1 == 0:
        return int(data)

    return WRONG_VALUE


class DataclassMixin:
    @classmethod
    def fields(cls):
        return fields(cls)

    @classmethod
    def create(cls, **data) -> Self:
        return from_data(cls, data)

    @classmethod
    def create_strictly(cls, **data) -> Self:
        fields_ = {f.name for f in cls.fields()}
        for k in data:
            if k not in fields_:
                raise ValueError(f'Invalid field: {k}')
        return from_data(cls, data)

    @classmethod
    def create_from_camel_case_json(cls, data: dict) -> Self:
        return from_data(cls, to_snake_case_data(data))

    @classmethod
    def create_from_object(cls, obj) -> Self:
        if isinstance(obj, dict):
            raise ValueError('dict object should use create(**dict) or create_from_camel_case_json(dict)')
        if isinstance(obj, BASE_VALUE_TYPES):
            raise ValueError(f'Invalid object type: {type(obj)}, should not be one of {BASE_VALUE_TYPES}')
        return from_data(cls, {f.name: getattr(obj, f.name, MISSING) for f in fields(cls)})

    def to_camel_case_json(self) -> dict:
        return to_camel_case_json(self)

    def to_snake_case_json(self) -> dict:
        return to_snake_case_json(self)

    def serialize(self) -> dict:
        return _asdict(self, dict_factory=lambda f: {k: to_data(v) for k, v in f})

    def replace(self, **changes) -> Self:
        data = {f.name: getattr(self, f.name) for f in self.fields()}
        for k in changes:
            if k not in data:
                raise ValueError(f'Invalid field: {k}')
        data.update(changes)
        return from_data(type(self), data)
