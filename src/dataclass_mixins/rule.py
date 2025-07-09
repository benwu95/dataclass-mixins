from dataclasses import dataclass
from enum import Enum

from .dataclass_mixin import DataclassMixin


class NumberOperator(Enum):
    EQUAL = 'EQUAL'
    NOT_EQUAL = 'NOT_EQUAL'
    GREATER = 'GREATER'
    GREATER_EQUAL = 'GREATER_EQUAL'
    LESS = 'LESS'
    LESS_EQUAL = 'LESS_EQUAL'


class StringOperator(Enum):
    EQUAL = 'EQUAL'
    NOT_EQUAL = 'NOT_EQUAL'
    STARTS = 'STARTS'
    NOT_STARTS = 'NOT_STARTS'
    ENDS = 'ENDS'
    NOT_ENDS = 'NOT_ENDS'
    CONTAINS = 'CONTAINS'
    NOT_CONTAINS = 'NOT_CONTAINS'


number_operators = [o.value for o in NumberOperator]
string_operators = [o.value for o in StringOperator]


@dataclass(frozen=True)
class Expression(DataclassMixin):
    field: str
    operator: str
    value: list[str] | int | float

    def __post_init__(self):
        if self.operator not in number_operators + string_operators:
            raise ValueError(f'Invalid operator: {self.operator}')
        if isinstance(self.value, (int, float)) and self.operator not in number_operators:
            raise ValueError(f'Invalid operator: {self.operator}, must be one of {number_operators}')
        if isinstance(self.value, list) and self.operator not in string_operators:
            raise ValueError(f'Invalid operator: {self.operator}, must be one of {string_operators}')

    def verify(self, obj) -> bool:
        value = obj
        for f in self.field.split('.'):
            value = getattr(value, f, None)

        if (
            self.operator in number_operators
            and isinstance(value, (int, float))
            and isinstance(self.value, (int, float))
        ):
            if self.operator == NumberOperator.EQUAL.value:
                return value == self.value
            if self.operator == NumberOperator.NOT_EQUAL.value:
                return value != self.value
            if self.operator == NumberOperator.GREATER.value:
                return value > self.value
            if self.operator == NumberOperator.GREATER_EQUAL.value:
                return value >= self.value
            if self.operator == NumberOperator.LESS.value:
                return value < self.value
            if self.operator == NumberOperator.LESS_EQUAL.value:
                return value <= self.value

        if (
            self.operator in string_operators
            and isinstance(value, str)
            and isinstance(self.value, list)
        ):
            if self.operator == StringOperator.EQUAL.value:
                return value in self.value
            if self.operator == StringOperator.NOT_EQUAL.value:
                return value not in self.value
            if self.operator == StringOperator.STARTS.value:
                return any(value.startswith(v) for v in self.value)
            if self.operator == StringOperator.NOT_STARTS.value:
                return all(not value.startswith(v) for v in self.value)
            if self.operator == StringOperator.ENDS.value:
                return any(value.endswith(v) for v in self.value)
            if self.operator == StringOperator.NOT_ENDS.value:
                return all(not value.endswith(v) for v in self.value)
            if self.operator == StringOperator.CONTAINS.value:
                return any(v in value for v in self.value)
            if self.operator == StringOperator.NOT_CONTAINS.value:
                return all(v not in value for v in self.value)

        return False


@dataclass(frozen=True)
class Rule(DataclassMixin):
    expressions: list[Expression]

    def verify(self, obj) -> bool:
        return all(exp.verify(obj) for exp in self.expressions)
