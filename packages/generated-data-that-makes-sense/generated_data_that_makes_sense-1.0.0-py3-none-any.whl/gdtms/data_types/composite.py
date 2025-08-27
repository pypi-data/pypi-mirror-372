import typing as t

from gdtms.data_types.data_type import DataType
from gdtms.entities.field import Field


class Composite(DataType):
    def __init__(self, types: t.List[DataType]):
        self._types = types

    def set_field(self, field: "Field"):
        for type in self._types:
            type.set_field(field)

    @property
    def value(self):
        return " ".join([str(type.value) for type in self._types])
