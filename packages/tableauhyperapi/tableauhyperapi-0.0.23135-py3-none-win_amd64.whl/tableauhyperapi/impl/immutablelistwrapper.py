class ImmutableListWrapper:
    """ Simple wrapper around builtin list which does not allow list modification. """

    def __init__(self, real_list: list):
        self.__real_list = real_list

    def copy(self):
        return self.__real_list.copy()

    def __iter__(self):
        return self.__real_list.__iter__()

    def __len__(self):
        return self.__real_list.__len__()

    def __str__(self):
        return self.__real_list.__str__()

    def index(self, *args, **kwargs):
        return self.__real_list.index(*args, **kwargs)

    def count(self, arg):
        return self.__real_list.count(arg)

    def __getitem__(self, arg):
        return self.__real_list.__getitem__(arg)

    def __contains__(self, arg):
        return self.__real_list.__contains__(arg)

    def __eq__(self, arg):
        return self.__real_list.__eq__(arg)

    def __ne__(self, arg):
        return self.__real_list.__ne__(arg)
