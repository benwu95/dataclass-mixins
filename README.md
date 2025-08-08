# DataclassMixin
An extension to Python's dataclasses that provides type validation and common data conversion functions.
```python
from dataclasses import dataclass

from dataclass_mixins import DataclassMixin


@dataclass(frozen=True)
class A(DataclassMixin):
    a_a: int
    b_b: str


a = A.create()
a = A.create_strictly(a=1, b='b')

a.serialize()
# {'a_a': 1, 'b_b': 'b'}

a.to_camel_case_json()
# {'aA': 1, 'bB': 'b'}
```

## Coverage
|File|Stmts|Miss|Cover(%)|Missing|
|---|---|---|---|---|
|[dataclass_mixin.py](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/dataclass_mixin.py)|246|2|99.19|[27](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/dataclass_mixin.py#L27), [202](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/dataclass_mixin.py#L202)|
|[rule.py](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/rule.py)|73|1|98.63|[90](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/rule.py#L90)|
|TOTAL|319|3|99.07||

## Creation
### Default Values
When a field is not assigned a value, the default value will be determined based on the following conditions:
1. Use the `default` or `default_factory` defined in the field
2. If the field has multiple types and includes `None`, the default value will be `None`
3. If the first type of the field is `list`, `set`, or `dict`, create the corresponding container
4. If the first type of the field is a `dataclass`, create an empty `dataclass`
5. If none of the above conditions are met, the default value will be `None`

### Data Validation
- During creation, the type of provided parameters will be checked against the types defined in the dataclass
- `DataclassMixin.create_strictly()` will check if parameter names match the dataclass fields

## Conversion Functions
### JSON/object to dataclass
Convert data to dataclass as much as possible
- value to value
- `dict` or custom class to dataclass
- value to `Enum`
- `int`, `float`, `Decimal`, or date `str` to `datetime`

Special handling for the following cases:
- `Enum` to value: Check if the value matches the type
- `datetime` to `int`: Convert to `int(timestamp())`
- `datetime` to `float` or `Decimal`: Convert to `timestamp()`

#### `DataclassMixin.create()`
Standard kwargs format

#### `DataclassMixin.create_strictly()`
Works the same as `DataclassMixin.create()`, but checks if parameter names match dataclass fields

#### `DataclassMixin.create_from_camel_case_json()`
Convert camel case JSON to dataclass, for example, converting frontend payload to dataclass

#### `DataclassMixin.create_from_object()`
- Convert object to dataclass, for example, converting entity to API response dataclass
- Will raise error if object type is `dict`, suggesting to use `create()` or `create_from_camel_case_json()`
- Will raise error if object type is in `str, int, float, bool, datetime, Enum, list, tuple, set`

### Dataclass to JSON
Use `dataclasses.asdict()` for conversion, with special handling for:
- `Enum`: Convert to `value`
- `datetime`: Convert to `timestamp()`

#### `DataclassMixin.serialize()`
Basic conversion

#### `DataclassMixin.to_camel_case_json()`
Convert all field names to camel case

#### `DataclassMixin.to_snake_case_json()`
Convert all field names to snake case

## Development
```sh
pip install -r tests/requirements.txt
PYTHONPATH=./ pytest --cov=src/ --cov-report=term-missing tests -vv -s
```
