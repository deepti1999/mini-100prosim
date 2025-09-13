from .value_factory import *

"""
ValueCollection is a dedicated ValueFactory caching all values which had ever been retrieved
"""


class ValueCollection(ValueFactory):

    def __init__(self, vf: ValueFactory):
        self.__valueFactory = vf  # value factory for new values
        self.__values = {}        # dictionary with values

    def value(self, vid) -> Value:
        if self.__values.get(vid) is None:   # check if value is already existing in dictionary
            new_value = self.__valueFactory.value(vid)
            if new_value is not None:
                new_value.value_factory = self   # make value collection known to value
                self.__values[vid] = new_value
            else:
                return None

        if self.__values.get(vid) is not None:
            return self.__values[vid]

    @property
    def values(self):
        return self.__values
