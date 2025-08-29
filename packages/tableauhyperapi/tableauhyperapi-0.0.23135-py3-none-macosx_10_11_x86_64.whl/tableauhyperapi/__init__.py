"""
tableauhyperapi - a Hyper client library.

This library allows spawning a local Hyper server instance, connecting to a Hyper server, running queries and commands,
and writing data into database tables.

tableauhyperapi classes are implemented in submodules of the tableauhyperapi package, however those submodules are
considered a private implementation detail, and there are no stability guarantees for them. Only symbols exported
from the top-level tableauhyperapi package constitute the stable public API.

Sample usage
------------

Create a database and push some data into it:

.. testsetup:: tableauhyperapi.__init__

    import os
    if os.path.exists('mydb.hyper'):
        os.remove('mydb.hyper')

.. testcode:: tableauhyperapi.__init__

    from tableauhyperapi import HyperProcess, Connection, TableDefinition, SqlType, Telemetry, Inserter, CreateMode

    # Start a new private local Hyper instance
    with HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp') as hyper:
        # Create the extract, replace it if it already exists
        with Connection(hyper.endpoint, 'mydb.hyper', CreateMode.CREATE_AND_REPLACE) as connection:
            schema = TableDefinition('foo', [
                TableDefinition.Column('a', SqlType.text()),
                TableDefinition.Column('b', SqlType.big_int()),
            ])
            connection.catalog.create_table(schema)
            with Inserter(connection, schema) as inserter:
                inserter.add_rows([
                    ['x', 1],
                    ['y', 2],
                ])
                inserter.execute()

Connect to an existing extract and append data to a table in it:

.. testsetup:: tableauhyperapi.__init__2

    from tableauhyperapi import *
    hyper = HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp')

.. testcode:: tableauhyperapi.__init__2

    with Connection(hyper.endpoint, 'mydb.hyper') as connection:
        with Inserter(connection, 'foo') as inserter:
            inserter.add_row(['z', 3])
            inserter.execute()

.. testcleanup:: tableauhyperapi.__init__2

    hyper.close()

Run some queries:

.. testsetup:: tableauhyperapi.__init__3

    from tableauhyperapi import *
    hyper = HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp')
    connection = Connection(hyper.endpoint, 'mydb.hyper')

.. testcode:: tableauhyperapi.__init__3

    with connection.execute_query('SELECT * FROM foo') as result:
        rows = list(result)
        assert sorted(rows) == [['x', 1], ['y', 2], ['z', 3]]

        top_a = connection.execute_scalar_query('SELECT MAX(b) FROM foo')
        assert top_a == 3

        connection.execute_command('DROP TABLE foo')

.. testcleanup:: tableauhyperapi.__init__3

    connection.close()
    hyper.close()
    import os
    os.remove('mydb.hyper')


API Reference
-------------

.. autosummary::
    :nosignatures:

    tableauhyperapi.HyperException
    tableauhyperapi.HyperProcess
    tableauhyperapi.Connection
    tableauhyperapi.Endpoint
    tableauhyperapi.Catalog
    tableauhyperapi.Inserter
    tableauhyperapi.TableDefinition
    tableauhyperapi.Persistence
    tableauhyperapi.Result
    tableauhyperapi.ResultSchema
    tableauhyperapi.TypeTag
    tableauhyperapi.SqlType
    tableauhyperapi.Name
    tableauhyperapi.DatabaseName
    tableauhyperapi.SchemaName
    tableauhyperapi.TableName
    tableauhyperapi.Date
    tableauhyperapi.Timestamp
    tableauhyperapi.Interval
    tableauhyperapi.HyperServiceVersion

"""

from .catalog import Catalog
from .connection import Connection, CreateMode
from .databasename import DatabaseName
from .date import Date
from .endpoint import Endpoint
from .hyperexception import HyperException
from .hyperprocess import Telemetry, HyperProcess
from .hyperserviceversion import HyperServiceVersion
from .inserter import Inserter
from .interval import Interval
from .name import Name
from .result import Result
from .resultschema import ResultSchema
from .schemaname import SchemaName
from .sql import escape_name, escape_string_literal
from .sqltype import SqlType, TypeTag
from .tabledefinition import Nullability, Persistence, TableDefinition
from .tablename import TableName
from .timestamp import Timestamp
from .warning import UnclosedObjectWarning

NULLABLE = Nullability.NULLABLE
NOT_NULLABLE = Nullability.NOT_NULLABLE
PERMANENT = Persistence.PERMANENT
TEMPORARY = Persistence.TEMPORARY

__all__ = [
    'HyperException',
    'HyperProcess', 'Telemetry', 'Connection', 'Endpoint', 'CreateMode', 'Catalog',
    'Result', 'ResultSchema', 'Inserter', 'Persistence', 'Nullability', 'SqlType', 'TypeTag',
    'Name', 'SchemaName', 'TableName', 'DatabaseName', 'TableDefinition',
    'escape_name', 'escape_string_literal',
    'Date', 'Timestamp', 'Interval', 'UnclosedObjectWarning',
    'NULLABLE', 'NOT_NULLABLE',
    'PERMANENT', 'TEMPORARY', 'HyperServiceVersion'
]

try:
    from .impl import version
    VERSION = version.VERSION
    """ Version number of the library as a tuple `(major, minor, micro)`. """
    __version__ = version.__version__
    """ PEP-396-compliant version number of the library. """
except ImportError:
    # impl/version.py is a generated file, use all zeros when running from the source directory.
    VERSION = (0, 0, 0)
    __version__ = '0.0.0'
