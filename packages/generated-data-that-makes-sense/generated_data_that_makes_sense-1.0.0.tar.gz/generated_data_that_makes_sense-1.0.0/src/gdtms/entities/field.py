import typing as t
from random import randint

from gdtms.data_types.data_type import DataType
from gdtms.data_types.undefined import Undefined


class Field:
    def __init__(
        self,
        name: str,
        type: DataType = Undefined(),
        size: t.Optional[int] = None,
        chance_of_null: int = 0,
    ):
        self.title = name
        self.type = type
        self.size = size
        self.chance_of_null = chance_of_null

    def set_table(self, table: "Table"):
        self._table = table

    def get_table(self):
        return self._table

    def get_value(self):
        if self._is_null():
            return None
        type = self.type
        type.set_field(self)
        return self._normalize(type.value, self.size)

    def _normalize(self, value, size):
        if size and isinstance(value, str):
            return value[0:size]
        return value

    def _is_null(self) -> bool:
        if not self.chance_of_null:
            return False
        if randint(0, 100) >= self.chance_of_null:
            return False
        return True
