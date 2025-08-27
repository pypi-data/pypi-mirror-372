import string
from random import choice, randint

from gdtms.data_types.data_type import DataType
from gdtms.data_types.number import Number


class ZipPostal(DataType):
    @property
    def value(self):
        if choice([True, False]):
            return self._zip()
        return self._postal()

    def _postal(self):
        postal = ""
        for _ in range(3):
            postal += choice(string.ascii_letters).upper() + str(randint(0, 9))
        return postal[0:3] + " " + postal[3:]

    def _zip(self):
        return str(Number(min_number=10_000, max_number=99_999).value)
