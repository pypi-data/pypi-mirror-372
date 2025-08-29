import enum
from typing import Union, Optional, Iterable, Sequence, cast, overload

from .name import Name
from .sqltype import SqlType
from .tablename import TableName
from .impl import hapi
from .impl.immutablelistwrapper import ImmutableListWrapper
from .impl.util import check_precondition


class Nullability(enum.Enum):
    """
    Constants which define whether a column may contain NULL values.
    """

    NOT_NULLABLE = 0
    """ Column is not nullable, i.e., it may not contain NULL values. """

    NULLABLE = 1
    """ Column is nullable, i.e., it may contain NULL values. """

    @staticmethod
    def _from_bool_nullable(nullable: bool) -> 'Nullability':
        return Nullability.NULLABLE if nullable else Nullability.NOT_NULLABLE


class Persistence(enum.Enum):
    """
    Persistence type of a table.
    """

    PERMANENT = hapi.HYPER_PERMANENT
    """ Table is permanent, stored in the database on disk. """

    TEMPORARY = hapi.HYPER_TEMPORARY
    """
    Table is temporary. It is only visible to the connection that created the table and will be deleted
    once this connection is closed.
    """

    @staticmethod
    def _from_value(value: int):
        for v in Persistence:
            if v.value == value:
                return v
        raise ValueError(f'Invalid persistence value {value}')


class TableDefinition:
    """
    A SQL table definition.

    :param table_name: the table name.
    :param columns: an optional list of table columns.
    :param persistence: an optional persistence mode for the table, :any:`PERMANENT` by default.

    Examples:

    .. testsetup:: TableDefinition.__init__

        from tableauhyperapi import *

    .. testcode:: TableDefinition.__init__

        table_def = TableDefinition('products', [
            TableDefinition.Column('id', SqlType.int(), Nullability.NOT_NULLABLE),
            TableDefinition.Column('name', SqlType.text()),
            TableDefinition.Column('price', SqlType.double()),
        ])

        table_def.add_column('category', SqlType.text())

    """

    class Column:
        """
        An object which represents a table column.

        :param name: the column name.
        :param type: the column type.
        :param nullability: the optional column nullability, :any:`NULLABLE` by default.
        :param collation: the text column collation, ``None`` by default. ``None`` means default binary collation.
        """

        def __init__(self, name: Union[Name, str], type: SqlType,
                     nullability: Nullability = Nullability.NULLABLE,
                     collation: str = None):
            check_precondition(isinstance(type, SqlType), "'type' must be a SqlType instance")
            check_precondition(isinstance(nullability, Nullability), "'nullability' must be a Nullability instance")
            self.__name = Name(name)
            self.__type = type
            self.__nullability = nullability
            self.__collation = collation

        @property
        def name(self) -> Name:
            """ The name of the column. """
            return self.__name

        @property
        def type(self) -> SqlType:
            """ The type of the column. """
            return self.__type

        @property
        def nullability(self) -> Nullability:
            """ The nullability of the column. """
            return self.__nullability

        @property
        def collation(self) -> Optional[str]:
            """ The collation of the column. """
            return self.__collation

        def __repr__(self):
            collation = f'{self.__collation!r}' if self.__collation else ''
            cls_name = self.__class__.__name__
            namestr = self.__name.unescaped
            return f'{cls_name}({namestr!r}, {self.__type!r}, {self.__nullability!s}{collation})'

    def __init__(self, table_name: Union[Name, TableName, str],
                 columns: Optional[Iterable[Column]] = None,
                 persistence: Persistence = Persistence.PERMANENT):
        check_precondition(isinstance(persistence, Persistence),
                           "'persistence' must be a Persistence instance")
        self.__table_name = TableName(table_name)
        self.__columns = list(columns) if columns else []
        self.__immutable_columns = ImmutableListWrapper(self.__columns)
        self.__persistence = persistence

    @property
    def columns(self) -> Sequence[Column]:
        """  The list of table columns. This list cannot be modified, use :any:`add_column()` to add a new column. """
        return cast(Sequence['Column'], self.__immutable_columns)

    @property
    def column_count(self) -> int:
        """ The number of columns in the table. """
        return len(self.__columns)

    def get_column(self, position: int) -> Column:
        """
        Gets the column at the given position.

        :param position: column position, must be in the range from 0 to :any:`column_count` - 1.
        :return: the column.
        """
        check_precondition(0 <= position < len(self.__columns),
                           "'position' must be between 0 and {}".format(len(self.__columns) - 1))
        return self.__columns[position]

    def get_column_by_name(self, name: Union[str, Name]) -> Optional[Column]:
        """
        Gets the column with the given name if it exists.

        :param name: the column name.
        :return: the column, or None if it does not exist.
        """
        compare_name = Name(name)
        for col in self.__columns:
            if col.name == compare_name:
                return col
        return None

    def get_column_position_by_name(self, name: Union[str, Name]) -> Optional[int]:
        """
        Gets the position of the column with the given name.

        :param name: the column name.
        :return: the column position, or None if it does not exist.
        """
        compare_name = Name(name)
        for i, col in enumerate(self.__columns):
            if col.name == compare_name:
                return i
        return None

    @property
    def table_name(self) -> TableName:
        """ Returns the table name. """
        return self.__table_name

    @table_name.setter
    def table_name(self, name: Union[Name, TableName, str]):
        """ Sets table name. """
        self.__table_name = TableName(name)

    @property
    def persistence(self) -> Persistence:
        """ Returns the table's persistence mode. """
        return self.__persistence

    @persistence.setter
    def persistence(self, persistence: Persistence):
        """ Sets the table persistence mode. """
        check_precondition(isinstance(persistence, Persistence),
                           "'persistence' must be a Persistence instance")
        self.__persistence = persistence

    @overload
    def add_column(self, column: Column) -> 'TableDefinition':
        pass

    @overload
    def add_column(self, name: str, type: SqlType,
                   nullability: Nullability = Nullability.NULLABLE,
                   collation: str = None) -> 'TableDefinition':
        pass

    def add_column(self, *args, **kwargs) -> 'TableDefinition':
        """
        Adds a column. The parameters are either the :any:`Column` object to add, or arguments for the :any:`Column`
        constructor.

        :return: self.

        Examples:

        .. testsetup:: TableDefinition.add_column

            from tableauhyperapi import *
            table_def = TableDefinition('foo')

        .. testcode:: TableDefinition.add_column

            column = TableDefinition.Column("a", SqlType.int())
            table_def.add_column(column)

            table_def.add_column("b", SqlType.text(), collation='en_US_CI')

        """
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], TableDefinition.Column):
            column = args[0]
        else:
            column = TableDefinition.Column(*args, **kwargs)
        self.__columns.append(column)
        return self

    def _clone(self) -> 'TableDefinition':
        return TableDefinition(self.table_name, self.columns, self.persistence)

    def _for_list_of_columns(self, column_names: Iterable[str]) -> 'TableDefinition':
        columns = []
        for name in column_names:
            column = self.get_column_by_name(name)
            if column is None:
                raise ValueError('Column with name "{}" does not exist'.format(name))
            columns.append(column)
        return TableDefinition(self.table_name, columns, self.persistence)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}({self.__table_name!r}, {self.__columns!r}, {self.__persistence!s})'
