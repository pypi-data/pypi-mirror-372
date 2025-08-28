# Pytest Shared Session Fixture

[![image](https://img.shields.io/pypi/v/pytest-shared-session-scope)](https://pypi.org/project/pytest-shared-session-scope/)

Session scoped fixture that is shared between all workers in a pytest-xdist run.

<!--- doctest:main --->
```python
from pytest_shared_session_scope import shared_session_scope_json, CleanupToken, SetupToken

def expensive_calculation():
  return 123

def clean_up(data):
  print(f"Cleaning up {data}")

@shared_session_scope_json()
def my_fixture_return():
    return expensive_calculation()

@shared_session_scope_json()
def my_fixture():
    data = yield
    if data is SetupToken.FIRST:
        data = expensive_calculation()
    token: CleanupToken = yield data
    if token is CleanupToken.LAST:
      clean_up(data)

def test_return(my_fixture_return):
    assert my_fixture_return == 123

def test(my_fixture):
    assert my_fixture == 123
```

It differs from normal fixtures in two ways:
- If it yields it must yield twice - once to optionally calculate the value, once to yield the value to the test
- If it yields, a `SetupToken` or calculated data is send back in the first yield. This can be used to determine if the worker should do any the calulation or it has already been done.
- If it yields, a `CleanupToken` is send back in the second yield. This can be used to determine if the worker should do any cleanup.
- The data needs to be serializable somehow. The default implementation uses the built-in `json.dumps/json.loads` but custom serialization can be used.

If the fixture "just" returns a value it works too without any modifications.

## Why?

This helps avoid one of the most classic pytest pitfalls: session-scoped fixtures are run in each xdist worker.
This is a special case of the more general pytest pitfall of thinking that if something works, it will also work with xdist.


## Why Not?

The double yield makes them different from normal pytest fixtures and can be confusing.
The implementation is a bit hacky - we need to modify the signature of functions to pass fixture values to the inner actual fixture.
I'm also not entirely confident cleanup will work correctly in all cases.

## Known limitations

- Does not work correctly with the '-x' option or any option that makes it stop before running all tests.
- Does not work with tests that dynamically get a fixture value using `request.getfixturevalue()`

## Recipes

### Non JSON serializable data

The default store uses `json.dumps/json.loads` which cannot handle all objects. For arbitrary objects, you can use `shared_session_scope_pickle` which uses Python's pickle module:

<!--- doctest:pickle --->
```python
from pytest_shared_session_scope import shared_session_scope_pickle, SetupToken

class CustomObject:
    def __init__(self, value):
        self.value = value

@shared_session_scope_pickle()
def my_fixture():
    object_instance = yield
    if object_instance is SetupToken.FIRST:
        object_instance = CustomObject(42)
    yield object_instance

def test_custom_object(my_fixture):
    assert isinstance(my_fixture, CustomObject)
    assert my_fixture.value == 42
```

Alternatively, you can use the `serialize` and `deserialize` arguments with `shared_session_scope_json`:

<!--- doctest:non-serializable --->
```python
from pytest_shared_session_scope import shared_session_scope_json
from datetime import datetime

def serialize(value: datetime) -> str:
    return value.isoformat()

def deserialize(value: str) -> datetime:
    return datetime.fromisoformat(value)

@shared_session_scope_json(serialize=serialize, deserialize=deserialize)
def my_fixture_return():
    return datetime.now()

def test_datetime(my_fixture_return):
    assert isinstance(my_fixture_return, datetime)

```

You might also want to parse it into something before returning it to the test.
This can be useful when you want to yield/return a non-serializable object to the test, but still need to store it in a serializable format.

<!--- doctest:non-serializable-parse --->
```python
from pytest_shared_session_scope import shared_session_scope_fixture, SetupToken
from pytest_shared_session_scope.store import FileStore 

import json

def deserialize(value: str) -> dict:
    return json.loads(value)

def serialize(value: dict) -> str:
    return json.dumps(value)

class Connection:
    def __init__(self, port: int):
        self.port = port

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@shared_session_scope_fixture(
    store=FileStore(),
    parse=Connection.from_dict,
    serialize=serialize,
    deserialize=deserialize,
)
def connection():
    data = yield
    if data is SetupToken.FIRST:
        data = {"port": 123}
    yield data

def test_connection(connection):
    assert connection.port is 123
    assert isinstance(connection, Connection)
```

The general rules are:
- The fixture should yield sufficient information (data) to create the object you want to use in the test
- The `parse` function should take that data and from it create the object you want to use in the test
- The `serialize` function should take data and return a type that can be saved to the store
- The `deserialize` function should take the serialized data and return the data you want to parse

In most cases, you don't have to care about this.

### Implementing and using a custom store

The default stores saves data as string to a local filsystem. If you want to use a different store, you can implement your own. It needs to follow the protocol defined with `pytest_shared_session_scope.types.Store`.
Mainly it needs to implement three methods:

- `read` to read the data from the store
- `write` to write the data to the store
- `lock` to lock the store to ensure no race conditions.

Usually you want to store the data on the local filesystem. There's a mixin for that: `LocalFileStoreMixin`. It has a helper method `_get_path` that returns a path to a file in a temporary directory and you just need to implement `read` and `write` methods. The store should be passed to the `shared_session_scope_fixture` decorator, which the `shared_session_scope_json` is just a wrapper around.
Below is an example of a store that uses Polars to read and write parquet files. 

<!--- doctest:custom-store --->
```python
from typing import Any
from pytest_shared_session_scope import shared_session_scope_fixture, SetupToken
import polars as pl

from pytest_shared_session_scope.store import LocalFileStoreMixin
from pytest_shared_session_scope.types import StoreValueNotExists


class PolarsStore(LocalFileStoreMixin):
    def read(self, identifier: str, fixture_values: dict[str, Any]) -> pl.DataFrame:
        path = self._get_path(identifier, fixture_values["tmp_path_factory"])
        try:
            return pl.read_parquet(path)
        except FileNotFoundError:
            raise StoreValueNotExists()

    def write(self, identifier: str, data: pl.DataFrame, fixture_values: dict[str, Any]):
        path = self._get_path(identifier, fixture_values["tmp_path_factory"])
        data.write_parquet(path)


@shared_session_scope_fixture(PolarsStore())
def my_fixture():
    data = yield
    if data is SetupToken.FIRST:
        data = pl.DataFrame({"a": [1, 2, 3]})
    yield data

def test_polars(my_fixture):
  assert isinstance(my_fixture, pl.DataFrame)
```

Attentive readers will notice that this could also be achieved with the default `FileStore` or even the `shared_session_scope_json` by creating clever serialization and deserialization functions. However here it's probably simpler to just use a custom store. Implementing this store with `deserialize`, `serialize` and `parse` is left up as an exercise for the reader.

### Returning functions

It's a common pattern to return functions from fixtures - for example to register data needed in the cleanup. Instead, use two fixtures - one to calculate the data and one to use it. But remember that the second fixture is run in each worker! So it won't cover all cases.

<!--- doctest:returning-functions --->
```python
import pytest
from pytest_shared_session_scope import shared_session_scope_json

@shared_session_scope_json()
def important_ids():
    return [1,2,3]

@pytest.fixture
def cleanup_important_ids(important_ids):
    ids_to_cleanup = []
    def use_id(id_):
      if id_ not in important_ids:
        raise ValueError(f"{id_} not in important_ids!")
      ids_to_cleanup.append(id_)
    yield use_id
    for id in ids_to_cleanup:
      print(f"Cleaning up {id}")

def test_thing_with_ids(important_ids, cleanup_important_ids):
    for id in important_ids:
      # assert thing
      cleanup_important_ids(id)
```

### Using with cache

Pytest has a built-in cache that can be used to store data between runs. This can be useful to avoid recalculating data between runs. 

<!--- doctest:cache --->
```python
from pytest_shared_session_scope import shared_session_scope_json, SetupToken

@shared_session_scope_json()
def my_fixture(pytestconfig):
    data = yield
    if data is SetupToken.FIRST:
        data = pytestconfig.cache.get("example/value", None)
        if data is None:
            data = {"hey": "data"}
            pytestconfig.cache.set("example/value", data)
    yield data


def test(my_fixture):
    assert my_fixture == {"hey": "data"}
```

## How?

The decorator is a generalization of the guide from the pytest-xdist docs of how to [make session scoped fixtures execute only once](https://pytest-xdist.readthedocs.io/en/stable/how-to.html#making-session-scoped-fixtures-execute-only-once) with the added feature of being able to run cleanup code in the last worker to finish. 
To summarize, the first worker to request the fixture will calculate it and them persist it in a `Store`. 
Other workers will load the data from the `Store`.
If these `Stores` needs access to other fixtures (say, `tmp_path_factory`) we modify the signature of the actual wrapped fixture to include these fixtures.

To keep count on what worker is the last to finish, we keep a running track of what tests has been run in each worker (using the 
`pytest_runtest_protocol` and `config.stash`). This information is then yielded back to the worker


