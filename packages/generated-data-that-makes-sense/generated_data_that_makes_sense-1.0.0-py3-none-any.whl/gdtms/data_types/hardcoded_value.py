from gdtms.data_types.data_type import DataType


class HadrcodedValue(DataType):
    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def value(self):
        return self._value
