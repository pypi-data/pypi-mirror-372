from pathlib import PurePath
from typing import Union

from .name import Name
from .impl.dllutil import invoke_native_string_transform_function
from .impl import hapi


def escape_name(identifier: Union[str, PurePath]) -> str:
    """
    Quotes and escapes an identifier for use in SQL queries..

    :param identifier: the identifier to quote.
    :return: a properly quoted and escaped string representing the name.

    Example:

    .. testsetup:: escape_name

        from tableauhyperapi import *

    .. doctest:: escape_name

        >>> print(escape_name('a table'))
        "a table"
        >>> print(f'DROP TABLE {escape_name("a table")}')
        DROP TABLE "a table"
    """
    return str(Name(identifier))


def escape_string_literal(literal: str) -> str:
    """
    Quotes and escapes a string literal for use in SQL queries.

    :param literal: the string to escape.
    :return: the quoted string, including the quotes.

    Example:

    .. testsetup:: escape_string_literal

        from tableauhyperapi import *

    .. doctest:: escape_string_literal

        >>> print(f'SELECT * FROM foo WHERE a = {escape_string_literal("abc")}')
        SELECT * FROM foo WHERE a = 'abc'
    """
    return invoke_native_string_transform_function(hapi.hyper_quote_sql_literal, literal)
