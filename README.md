# DataclassMixin
基於 Python 的 dataclasses 擴充，提供資料方面的型別驗證和常用的轉換函式
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
|[rule.py](https://github.com/benwu95/dataclass-mixins/blob/main/src/dataclass_mixins/rule.py)|73|0|100||
|TOTAL|319|2|99.38||

## 建立
### 預設值
欄位沒有賦值的狀況下，會依據下列情況而有不同的預設值
1. 根據欄位定義的 `default` 或 `default_factory` 建立預設值
2. 如果欄位有多個型別且其中包含 `None`，預設值則為 `None`
3. 欄位的第一個型別是 `list`, `set`, `dict`，會建立對應的容器
4. 欄位的第一個型別是 `dataclass`，會建立一個空的 `dataclass`
5. 如果上述狀況皆不符合，預設值則為 `None`

### 資料驗證
- 建立時會根據有提供的參數，檢查其型別是否有符合 dataclass 所設定的型別
- `DataclassMixin.create_strictly()` 會檢查參數名稱是否符合 dataclass 的欄位

## 轉換函式
### JSON/object to dataclass
將資料盡可能的轉換成 dataclass
- value to value
- `dict` or custom class to dataclass
- value to `Enum`
- `int`, `float`, `Decimal`, or date `str` to `datetime`

遇到下述的狀況會做特別的處理
- `Enum` to value: 判斷 value 是否符合型別
- `datetime` to `int`: 這個狀況會轉成 `int(timestamp())`
- `datetime` to `float` or `Decimal`: 這個狀況會轉成 `timestamp()`

#### `DataclassMixin.create()`
一般的 kwargs 形式

#### `DataclassMixin.create_strictly()`
使用方式跟 `DataclassMixin.create()` 一樣，但是會檢查參數名稱是否符合 dataclass 的欄位

#### `DataclassMixin.create_from_camel_case_json()`
將 camel case 的 JSON 轉成 dataclass，例如把前端的 payload 轉成 dataclass

#### `DataclassMixin.create_from_object()`
- 將 object 轉成 dataclass，例如把 entity 轉成 api response 的 dataclass
- object 的型別如果是 `dict` 會出錯，並提示應該改成 `create()` 或 `create_from_camel_case_json()`
- object 的型別如果屬於 `str, int, float, bool, datetime, Enum, list, tuple, set` 會出錯

### Dataclass to JSON
使用 `dataclasses.asdict()` 轉換，遇到下述的型別會做特別的處理
- `Enum`: 轉成 `value`
- `datetime`: 轉成 `timestamp()`

#### `DataclassMixin.serialize()`
基本的轉換

#### `DataclassMixin.to_camel_case_json()`
將所有的欄位名稱轉成 camel case

#### `DataclassMixin.to_snake_case_json()`
將所有的欄位名稱轉成 snake case

## 開發測試
```sh
pip install -r tests/requirements.txt
PYTHONPATH=./ pytest --cov=src/ --cov-report=term-missing tests -vv -s
```
