from dataclasses import dataclass

import pytest

from src.dataclass_mixins.rule import NumberOperator, StringOperator, Expression, Rule


@dataclass
class Human:
    age: int
    name: str


@dataclass
class HumanWithWrongDataType:
    age: str
    name: int


obj = Human(age=30, name='Alice')


def test_expression_number_equal():
    exp = Expression(field='age', operator=NumberOperator.EQUAL.value, value=30)
    assert exp.verify(obj)


def test_expression_number_not_equal():
    exp = Expression(field='age', operator=NumberOperator.NOT_EQUAL.value, value=1)
    assert exp.verify(obj)


def test_expression_number_greater():
    exp = Expression(field='age', operator=NumberOperator.GREATER.value, value=20)
    assert exp.verify(obj)


def test_expression_number_greater_equal():
    exp = Expression(field='age', operator=NumberOperator.GREATER_EQUAL.value, value=30)
    assert exp.verify(obj)


def test_expression_number_less():
    exp = Expression(field='age', operator=NumberOperator.LESS.value, value=40)
    assert exp.verify(obj)


def test_expression_number_less_equal():
    exp = Expression(field='age', operator=NumberOperator.LESS_EQUAL.value, value=30)
    assert exp.verify(obj)


def test_expression_string_equal():
    exp = Expression(field='name', operator=StringOperator.EQUAL.value, value=['Alice'])
    assert exp.verify(obj)


def test_expression_string_not_equal():
    exp = Expression(field='name', operator=StringOperator.NOT_EQUAL.value, value=['Bob'])
    assert exp.verify(obj)


def test_expression_string_starts():
    exp = Expression(field='name', operator=StringOperator.STARTS.value, value=['Al'])
    assert exp.verify(obj)


def test_expression_string_not_starts():
    exp = Expression(field='name', operator=StringOperator.NOT_STARTS.value, value=['Bo'])
    assert exp.verify(obj)


def test_expression_string_ends():
    exp = Expression(field='name', operator=StringOperator.ENDS.value, value=['ice'])
    assert exp.verify(obj)


def test_expression_string_not_ends():
    exp = Expression(field='name', operator=StringOperator.NOT_ENDS.value, value=['ob'])
    assert exp.verify(obj)


def test_expression_string_contains():
    exp = Expression(field='name', operator=StringOperator.CONTAINS.value, value=['lic'])
    assert exp.verify(obj)


def test_expression_string_not_contains():
    exp = Expression(field='name', operator=StringOperator.NOT_CONTAINS.value, value=['Bob'])
    assert exp.verify(obj)


def test_rule_verify():
    exps = [
        Expression(field='age', operator=NumberOperator.GREATER.value, value=20),
        Expression(field='name', operator=StringOperator.EQUAL.value, value=['Alice'])
    ]
    rule = Rule(expressions=exps)
    assert rule.verify(obj)


def test_rule_verify_false():
    exps = [
        Expression(field='age', operator=NumberOperator.LESS.value, value=20),
        Expression(field='name', operator=StringOperator.EQUAL.value, value=['Bob'])
    ]
    rule = Rule(expressions=exps)
    assert not rule.verify(obj)

    assert not rule.verify(HumanWithWrongDataType(age='thirty', name=123))


def test_expression_invalid_operator():
    with pytest.raises(ValueError):
        Expression(field='age', operator='INVALID', value=10)

    with pytest.raises(ValueError):
        Expression(field='age', operator=NumberOperator.GREATER.value, value=['not a number'])

    with pytest.raises(ValueError):
        Expression(field='name', operator=StringOperator.STARTS.value, value=1)
