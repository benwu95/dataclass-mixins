import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Literal

import pytest
from pendulum.datetime import DateTime

from src.dataclass_mixins import DataclassMixin, snake_to_camel_case, camel_to_snake_case


FLOAT_DEFAULT = 1.0


class Status(Enum):
    A = 1
    B = 2
    C = 3


def get_1_0():
    return FLOAT_DEFAULT


@dataclass(frozen=True)
class A(DataclassMixin):
    status: Status | None
    status_histories: list[Status]
    now: datetime
    now2: DateTime | None
    ASAP: Literal['A', 'B', Status.A] | None
    ASAP2: Literal['A', 'B', Status.A, None]
    is_TEST: Any
    more_than_two_type: list | tuple | set | dict | str | int
    int_or_none: int | None
    str_or_enum: str | Enum
    enum_to_value: int | None
    datetime_to_int: int | None
    datetime_to_float: float | None
    datetime_to_decimal: Decimal | None
    float_default: float | None = FLOAT_DEFAULT
    float_default_factory: float = field(default_factory=get_1_0)


class AA:
    def __init__(
        self,
        status,
        status_histories,
        now,
        now2,
        ASAP,
        ASAP2,
        is_TEST,
        more_than_two_type,
        int_or_none,
        str_or_enum,
        enum_to_value,
        datetime_to_int,
        datetime_to_float,
        datetime_to_decimal,
        float_default,
        float_default_factory
    ):
        self.status = status
        self.status_histories = status_histories
        self.now = now
        self.now2 = now2
        self.ASAP = ASAP
        self.ASAP2 = ASAP2
        self.is_TEST = is_TEST
        self.more_than_two_type = more_than_two_type
        self.int_or_none = int_or_none
        self.str_or_enum = str_or_enum
        self.enum_to_value = enum_to_value
        self.datetime_to_int = datetime_to_int
        self.datetime_to_float = datetime_to_float
        self.datetime_to_decimal = datetime_to_decimal
        self.float_default = float_default
        self.float_default_factory = float_default_factory


@dataclass(frozen=True)
class B(DataclassMixin):
    i_i: int
    s_s: str
    dataclass: A
    not_frozen_or_none: 'NotFrozen | None'  # also test forward references


@dataclass
class NotFrozen(DataclassMixin):
    i_i: int


class BB:
    def __init__(self, i_i, s_s, dataclass, not_frozen_or_none):
        self.i_i = i_i
        self.s_s = s_s
        self.dataclass = dataclass
        self.not_frozen_or_none = not_frozen_or_none


@dataclass(frozen=True)
class C(DataclassMixin):
    tuple_or_none: tuple[A, B] | None
    list_or_none: list[A] | None
    dict_or_none: dict[str, A] | None


class CC:
    def __init__(self, tuple_or_none, list_or_none, dict_or_none):
        self.tuple_or_none = tuple_or_none
        self.list_or_none = list_or_none
        self.dict_or_none = dict_or_none


@dataclass(frozen=True)
class D(DataclassMixin):
    tuple_dataclass: tuple[A, B, C]
    list_dataclass: list[C]
    dict_dataclass: dict[str, C]
    set_str: set[str]


class DD:
    def __init__(self, tuple_dataclass, list_dataclass, dict_dataclass, set_str):
        self.tuple_dataclass = tuple_dataclass
        self.list_dataclass = list_dataclass
        self.dict_dataclass = dict_dataclass
        self.set_str = set_str


@dataclass(frozen=True)
class E(DataclassMixin):
    tuple_int_str: tuple[int, str]
    list_str: list[str]
    dict_int_str: dict[int, str]


@dataclass(frozen=True)
class F(DataclassMixin):
    name: str
    info: dict


@dataclass(frozen=True)
class F1Info(DataclassMixin):
    a: int
    b: str


@dataclass(frozen=True)
class F1(F):
    name: Literal['F1']
    info: F1Info


@dataclass(frozen=True)
class F2Info(DataclassMixin):
    a: str
    b: int


@dataclass(frozen=True)
class F2(F):
    name: Literal['F2']
    info: F2Info


@dataclass(frozen=True)
class G(DataclassMixin):
    f: F1 | F2 | F


@dataclass(frozen=True)
class H(DataclassMixin):
    d: Decimal
    f: float
    i: int


now = datetime.now(timezone.utc)
now2 = DateTime.now('UTC')

test_a1 = A.create_strictly(
    status=Status.A,
    status_histories=[Status.A, Status.B],
    now=now,
    now2=now2,
    ASAP='A',
    ASAP2='B',
    is_TEST='A',
    more_than_two_type={},
    int_or_none=1,
    str_or_enum='2',
    enum_to_value=Status.C.value,
    datetime_to_int=int(now.timestamp()),
    datetime_to_float=now.timestamp(),
    datetime_to_decimal=Decimal(now.timestamp()),
    float_default=0.1,
    float_default_factory=2.0
)
test_a2 = A.create_strictly(status_histories=[Status.B, Status.C], now=now, ASAP=Status.A, is_TEST='B', str_or_enum='5')
test_b = B.create_strictly(i_i=4, s_s='5', dataclass=test_a1, not_frozen_or_none=None)
test_c1 = C.create_strictly(tuple_or_none=(test_a1, test_b), list_or_none=[test_a1, test_a2], dict_or_none={'a1': test_a1, 'a2': test_a2})
test_c2 = C.create()
test_d = D.create_strictly(tuple_dataclass=(test_a1, test_b, test_c1), list_dataclass=[test_c1, test_c2], dict_dataclass={'c1': test_c1, 'c2': test_c2}, set_str={'a', 'b'})

test_aa1 = AA(
    status=Status.A,
    status_histories=[1, 2],
    now=now,
    now2=now2,
    ASAP='A',
    ASAP2='B',
    is_TEST='A',
    more_than_two_type={},
    int_or_none=1,
    str_or_enum='2',
    enum_to_value=Status.C,
    datetime_to_int=now,
    datetime_to_float=now,
    datetime_to_decimal=now,
    float_default=0.1,
    float_default_factory=2.0
)
test_aa2 = AA(
    status=None,
    status_histories=[2, 3],
    now=now.timestamp(),
    now2=None,
    ASAP=Status.A.value,
    ASAP2=None,
    is_TEST='B',
    more_than_two_type=[],
    int_or_none=None,
    str_or_enum='5',
    enum_to_value=None,
    datetime_to_int=None,
    datetime_to_float=None,
    datetime_to_decimal=None,
    float_default=FLOAT_DEFAULT,
    float_default_factory=get_1_0()
)
test_bb = BB(i_i=4, s_s='5', dataclass=test_aa1, not_frozen_or_none=None)
test_cc1 = CC(tuple_or_none=(test_aa1, test_bb), list_or_none=[test_aa1, test_aa2], dict_or_none={'a1': test_aa1, 'a2': test_aa2})
test_cc2 = CC(tuple_or_none=None, list_or_none=None, dict_or_none=None)
test_dd = DD(tuple_dataclass=(test_aa1, test_bb, test_cc1), list_dataclass=[test_cc1, test_cc2], dict_dataclass={'c1': test_cc1, 'c2': test_cc2}, set_str={'a', 'b'})


def test_snake_to_camel_case():
    assert snake_to_camel_case('a1a_b1b') == 'a1aB1b'
    assert snake_to_camel_case('aa_BB') == 'aaBB'
    assert snake_to_camel_case('a') == 'a'

    # special case
    assert snake_to_camel_case('AA_bb') == 'AABb'
    assert snake_to_camel_case('AB') == 'AB'

    # pascal case
    assert snake_to_camel_case('Aa_Bb') == 'aaBb'


def test_camel_to_snake_case():
    assert camel_to_snake_case('a1aB1b') == 'a1a_b1b'
    assert camel_to_snake_case('aaBB') == 'aa_BB'
    assert camel_to_snake_case('A') == 'a'
    assert camel_to_snake_case('a') == 'a'

    # special case
    assert camel_to_snake_case('AABb') == 'AA_bb'
    assert camel_to_snake_case('AB') == 'AB'

    # pascal case
    assert camel_to_snake_case('AaBb') == 'aa_bb'


def test_json():
    data_1 = test_a1.serialize()
    json.dumps(data_1)

    assert test_a1.serialize() == test_a1.to_snake_case_json()


def test_field_default_data():
    assert [f.name for f in A.fields()] == [
        'status',
        'status_histories',
        'now',
        'now2',
        'ASAP',
        'ASAP2',
        'is_TEST',
        'more_than_two_type',
        'int_or_none',
        'str_or_enum',
        'enum_to_value',
        'datetime_to_int',
        'datetime_to_float',
        'datetime_to_decimal',
        'float_default',
        'float_default_factory'
    ]

    data_1 = test_a1.serialize()
    data_1.pop('float_default')
    data_1.pop('float_default_factory')
    assert A.create(**data_1).float_default == FLOAT_DEFAULT
    assert A.create(**data_1).float_default_factory == get_1_0()


def test_from_data():
    # test numbers
    H.create(d=1, f=1, i=1)
    H.create(d=1.0, f=1.0, i=1.0)
    H.create(d=Decimal(1), f=Decimal(1), i=Decimal(1))

    # test Literal
    with pytest.raises(ValueError):
        A.create(ASAP=Status.B)

    # D is not in Status
    with pytest.raises(ValueError):
        A.create(status='D')

    # datetime only accept datetime object, number or date str
    A.create(now=now)
    A.create(now=now.timestamp())
    A.create(now=int(now.timestamp()))
    A.create(now=Decimal(now.timestamp()))
    A.create(now=now.isoformat())
    a = A.create(now='20250722')
    assert a.now.tzinfo == timezone.utc
    with pytest.raises(ValueError):
        A.create(now='A')

    # more_than_two_type does not contain float
    with pytest.raises(ValueError):
        A.create(more_than_two_type=1.5)

    # i_i is int
    with pytest.raises(ValueError):
        B.create(i_i=1.5)

    # test list with wrong args type
    with pytest.raises(ValueError):
        E.create(list_str=['a', 1])
    with pytest.raises(ValueError):
        D.create(list_dataclass=[C.create(), 1])

    # test tuple with wrong args type
    with pytest.raises(ValueError):
        E.create(tuple_int_str=('a', 1))

    d = D.create(tuple_dataclass=(A.create(), B.create(), B.create()))
    assert d.tuple_dataclass == (A.create(), B.create(), C.create())

    # test dict keys with wrong args type
    with pytest.raises(ValueError):
        E.create(dict_int_str={'a': 'a'})
    with pytest.raises(ValueError):
        D.create(dict_dataclass={'a': C.create(), 2: C.create()})

    # test dict values with wrong args type
    with pytest.raises(ValueError):
        E.create(dict_int_str={1: 1})
    with pytest.raises(ValueError):
        D.create(dict_dataclass={'a': C.create(), 'b': 1})

    # test field with multiple dataclass
    g1 = G.create(f={'name': 'F1', 'info': {'a': 1, 'b': 'b'}})
    assert isinstance(g1.f, F1)
    g2 = G.create(f={'name': 'F2', 'info': {'a': 'a', 'b': 2}})
    assert isinstance(g2.f, F2)
    g = G.create(f={'name': 'F1', 'info': {'a': 'a', 'b': 'b'}})
    assert type(g.f) is F
    g = G.create(f={})
    assert type(g.f) is F

    with pytest.raises(ValueError):
        G.create(f={'name': 1, 'info': {'a': 1, 'b': 2}})


def test_create_empty():
    empty_a = A.create()
    assert empty_a.status is None
    assert empty_a.more_than_two_type == []

    empty_b = B.create()
    assert empty_b.i_i is None
    assert empty_b.s_s is None
    assert isinstance(empty_b.dataclass, A)
    assert empty_b.not_frozen_or_none is None

    empty_c = C.create()
    assert empty_c.tuple_or_none is None
    assert empty_c.list_or_none is None
    assert empty_c.dict_or_none is None

    empty_d = D.create()
    assert empty_d.tuple_dataclass is None
    assert empty_d.list_dataclass == []
    assert empty_d.dict_dataclass == {}
    assert empty_d.set_str == set()


def test_create_strictly():
    with pytest.raises(ValueError):
        A.create_strictly(a=1)


def test_create_from_object():
    b = B.create(i_i=4, s_s='5', dataclass=test_a1, not_frozen_or_none=NotFrozen(1))
    b2 = B.create_from_object(b)
    b2.not_frozen_or_none.i_i = 2
    assert b.not_frozen_or_none.i_i == 1

    # test wrong object type
    with pytest.raises(ValueError):
        A.create_from_object(1)
    with pytest.raises(ValueError):
        A.create_from_object({'a': 1})


def test_replace():
    b = test_b.replace(i_i=test_b.i_i + 1)
    assert b.i_i == test_b.i_i + 1
    assert b.dataclass == test_b.dataclass


def test_replace_failed():
    with pytest.raises(ValueError):
        test_b.replace(i_i='i_i')

    with pytest.raises(ValueError):
        test_b.replace(a=1)


def test_dataclass():
    assert test_a1 == A.create(**test_a1.serialize())
    assert test_a1 == A.create_from_camel_case_json(test_a1.to_camel_case_json())
    assert test_a1 == A.create_from_object(test_a1)
    assert test_a1 == A.create_from_object(test_aa1)


def test_dataclass_property():
    assert test_b == B.create(**test_b.serialize())
    assert test_b == B.create_from_camel_case_json(test_b.to_camel_case_json())
    assert test_b == B.create_from_object(test_b)
    assert test_b == B.create_from_object(test_bb)


def test_dataclass_in_container():
    assert test_c1 == C.create(**test_c1.serialize())
    assert test_c1 == C.create_from_camel_case_json(test_c1.to_camel_case_json())
    assert test_c1 == C.create_from_object(test_c1)
    assert test_c1 == C.create_from_object(test_cc1)

    assert test_d == D.create(**test_d.serialize())
    assert test_d == D.create_from_camel_case_json(test_d.to_camel_case_json())
    assert test_d == D.create_from_object(test_d)
    assert test_d == D.create_from_object(test_dd)
