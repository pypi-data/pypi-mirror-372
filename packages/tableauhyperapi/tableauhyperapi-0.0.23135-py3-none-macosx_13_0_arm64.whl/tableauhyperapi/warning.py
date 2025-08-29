class UnclosedObjectWarning(Warning):
    """ Warning issued when a :any:`HyperProcess`, :any:`Connection`, :any:`Result` or :any:`Inserter` object has
    not been properly closed (e.g., by a ``with`` statement or explicit ``shutdown()`` or ``close()`` method.)"""
