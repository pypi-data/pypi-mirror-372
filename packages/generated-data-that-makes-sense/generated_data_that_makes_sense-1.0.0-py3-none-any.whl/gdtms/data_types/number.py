from random import randint

from gdtms.data_types.data_type import DataType


class Number(DataType):
    def __init__(self, max_number: int, min_number: int = 0) -> None:
        self.max_number = max_number
        self.min_number = min_number

    @property
    def value(self):
        return randint(self.min_number, self.max_number)
