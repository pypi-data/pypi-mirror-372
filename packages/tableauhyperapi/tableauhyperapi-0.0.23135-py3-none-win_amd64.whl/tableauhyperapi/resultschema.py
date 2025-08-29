from typing import Union, Iterable, Optional, Tuple

from .name import Name
from .sqltype import SqlType
from .impl.util import check_precondition


class ResultSchema:
    """
    The schema of a query result. It consists of columns, which have a type and a name.
    """

    class Column:
        """
        A result column.
        """

        def __init__(self, name: Union[Name, str], type: SqlType):
            self.__name = Name(name)
            self.__type = type

        @property
        def name(self) -> Name:
            """ The name of the column. """
            return self.__name

        @property
        def type(self) -> SqlType:
            """ The type of the column. """
            return self.__type

        def __repr__(self):
            return f'{self.__class__.__name__}({self.__name.unescaped!r}, {self.__type!r})'

    def __init__(self, columns: Iterable[Column]):
        self.__columns = tuple(columns)

    @property
    def columns(self) -> Tuple[Column, ...]:
        """
        The list of the columns.
        """
        return self.__columns

    @property
    def column_count(self) -> int:
        """
        The column count.
        """
        return len(self.__columns)

    def get_column(self, position: int) -> Column:
        """
        Gets the column at the given position.

        :param position: column position, in the range from 0 to :any:`column_count`-1.
        :return: the column at the given index.
        """
        check_precondition(0 <= position < len(self.__columns),
                           "'position' must be in the range from 0 to {}".format(len(self.__columns) - 1))
        return self.__columns[position]

    def get_column_by_name(self, name: Union[Name, str]) -> Optional[Column]:
        """
        Gets the column with the given name, if it exists.

        :param name: the column name.
        :return: the column with the given name, or ``None`` if it does not exist.
        """
        idx = self.get_column_position_by_name(name)
        if idx is not None:
            return self.__columns[idx]
        return None

    def get_column_position_by_name(self, name: Union[str, Name]) -> Optional[int]:
        """
        Gets the position of the column with the given name, if it exists.

        :param name: the column name.
        :return: the column position, or ``None`` if it does not exist.
        """
        compare_name = Name(name)
        for i in range(len(self.__columns)):
            if self.__columns[i].name == compare_name:
                return i
        return None

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self.__columns)!r})'

    def __str__(self):
        cols = ', '.join(f'{x.name!s} {x.type!s}' for x in self.__columns)
        return f'Results Schema ( {cols} )'
