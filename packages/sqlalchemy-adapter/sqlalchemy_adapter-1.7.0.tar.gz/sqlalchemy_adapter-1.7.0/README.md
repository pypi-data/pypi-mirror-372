SQLAlchemy Adapter for PyCasbin 
====

[![build](https://github.com/officialpycasbin/sqlalchemy-adapter/actions/workflows/build.yml/badge.svg)](https://github.com/officialpycasbin/sqlalchemy-adapter/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/officialpycasbin/sqlalchemy-adapter/badge.svg)](https://coveralls.io/github/officialpycasbin/sqlalchemy-adapter)
[![Version](https://img.shields.io/pypi/v/sqlalchemy-adapter.svg)](https://pypi.org/project/sqlalchemy-adapter/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/sqlalchemy-adapter.svg)](https://pypi.org/project/sqlalchemy-adapter/)
[![Pyversions](https://img.shields.io/pypi/pyversions/sqlalchemy-adapter.svg)](https://pypi.org/project/sqlalchemy-adapter/)
[![Download](https://static.pepy.tech/badge/sqlalchemy-adapter)](https://pypi.org/project/sqlalchemy-adapter/)
[![License](https://img.shields.io/pypi/l/sqlalchemy-adapter.svg)](https://pypi.org/project/sqlalchemy-adapter/)

SQLAlchemy Adapter is the [SQLAlchemy](https://www.sqlalchemy.org) adapter for [PyCasbin](https://github.com/casbin/pycasbin). With this library, Casbin can load policy from SQLAlchemy supported database or save policy to it.

Based on [Officially Supported Databases](http://www.sqlalchemy.org/), The current supported databases are:

- PostgreSQL
- MySQL
- SQLite
- Oracle
- Microsoft SQL Server
- Firebird
- Sybase

## Installation

```
pip install sqlalchemy_adapter
```

## Simple Example

You can save and load policy to database.

```python
import sqlalchemy_adapter
import casbin

adapter = sqlalchemy_adapter.Adapter('sqlite:///test.db')

e = casbin.Enforcer('path/to/model.conf', adapter)

sub = "alice"  # the user that wants to access a resource.
obj = "data1"  # the resource that is going to be accessed.
act = "read"  # the operation that the user performs on the resource.

if e.enforce(sub, obj, act):
    # permit alice to read data1
    pass
else:
    # deny the request, show an error
    pass
```

By default, policies are stored in the `casbin_rule` table.
You can custom the table where the policy is stored by using the `table_name` parameter.

```python

import sqlalchemy_adapter
import casbin

custom_table_name = "<custom_table_name>"

# create adapter with custom table name.
adapter = sqlalchemy_adapter.Adapter('sqlite:///test.db', table_name=custom_table_name)

e = casbin.Enforcer('path/to/model.conf', adapter)
```


### Getting Help

- [PyCasbin](https://github.com/casbin/pycasbin)

### License

This project is licensed under the [Apache 2.0 license](LICENSE).
