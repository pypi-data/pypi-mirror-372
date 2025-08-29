import warnings
from typing import Optional

from .impl.util import check_precondition


class ContextId:
    """
    A context id.

    Used to identify the source of an exception. Each throw statement has a unique context id that is stored in the
    thrown error.
    """
    value: int

    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value:#x})'


class HyperException(Exception):
    """
    An exception raised by the Hyper API.
    Note that error messages may change in the future versions of the library.
    """

    main_message: Optional[str]
    hint: Optional[str]
    context_id: ContextId

    def __init__(
            self,
            context_id: ContextId,
            main_message: Optional[str] = None,
            hint: Optional[str] = None,
            message: Optional[str] = None,
            hint_message: Optional[str] = None):
        super().__init__(context_id,
                         main_message if main_message is not None else main_message,
                         hint if hint is not None else hint_message)

        if message:
            warnings.warn('Use `main_message` instead. This argument will be removed in the future.',
                          DeprecationWarning)
            check_precondition(main_message is None, 'When using the deprecated `message` parameter, the new '
                                                     '`main_message` parameter must not be set.')
            main_message = message

        if hint_message:
            warnings.warn('Use `hint` instead. This argument will be removed in the future.',
                          DeprecationWarning)
            check_precondition(hint is None, 'When using the deprecated `hint_message` parameter, the new `hint`'
                                             ' parameter must not be set.')
            hint = hint_message

        self.main_message = main_message
        """
        The main message of this exception.
        """
        self.context_id = context_id
        """
        A context ID. Each throw expression has a unique context id that is stored in the thrown error.
        """
        self.hint = hint
        """
        A possible hint on how to fix the error.
        """

    def __str__(self):
        """
        Returns the default string representation of this exception.

        The string is in the format ``<context>: <message>``.
        """
        s = ""
        if self.main_message:
            s += self.main_message.replace("\n", "\n\t")

        if self.hint:
            s += "\nHint: " + self.hint.replace("\n", "\n\t")

        s += "\nContext: " + hex(self.context_id.value & (2**32 - 1))

        if self.__cause__ is not None:
            s += "\n\nCaused by:\n"
            s += str(self.__cause__)

        return s

    @property
    def message(self) -> Optional[str]:
        """
        The main message of this exception.

        .. warning::
            Deprecated: Use :py:attr:`~main_message`
        """
        warnings.warn('Use `main_message` instead. This property will be removed in the future.', DeprecationWarning)
        return self.main_message

    @message.setter
    def message(self, message: Optional[str]):
        warnings.warn('Use `main_message` instead. This property will be removed in the future.', DeprecationWarning)
        self.main_message = message

    @property
    def hint_message(self) -> Optional[str]:
        """
        A possible hint on how to fix the error.

        .. warning::
            Deprecated: Use :py:attr:`~hint`
        """
        warnings.warn('Use `hint` instead. This property will be removed in the future.', DeprecationWarning)
        return self.hint

    @hint_message.setter
    def hint_message(self, hint_message: Optional[str]):
        warnings.warn('Use `hint` instead. This property will be removed in the future.', DeprecationWarning)
        self.hint = hint_message
