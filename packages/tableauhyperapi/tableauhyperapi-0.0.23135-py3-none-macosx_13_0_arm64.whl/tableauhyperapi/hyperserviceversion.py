class HyperServiceVersion:
    """
    A Hyper Service version number of the form 'major.minor'.
    :param major: The major part of the version number.
    :param minor: The minor part of the version number.
    """

    def __init__(self, major, minor):
        self.__major = major
        self.__minor = minor

    @property
    def major(self) -> int:
        """
        The major part of the version number.
        """
        return self.__major

    @property
    def minor(self) -> int:
        """
        The minor part of the version number.
        """
        return self.__minor

    def __repr__(self):
        return f'HyperServiceVersion({self.major}, {self.minor})'

    def __str__(self):
        return f'{self.major}.{self.minor}'

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, HyperServiceVersion):
            return self.major == other.major and self.minor == other.minor

        return NotImplemented

    def __hash__(self):
        return hash((self.major, self.minor))
