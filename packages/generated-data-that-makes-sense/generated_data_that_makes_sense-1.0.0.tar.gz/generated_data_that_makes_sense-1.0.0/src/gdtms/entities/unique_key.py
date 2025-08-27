import typing as t

from gdtms.entities.field import Field
from gdtms.entities.record import Record


class UniqueKey:
    def __init__(self, fields: t.List[Field]):
        self.fields = fields
        self._values = set()

    def set_table(self, table: "Table"):
        self.table = table

    def is_duplicate(self, record: Record) -> bool:
        key = self._get_key(record)
        return key in self._values

    def _get_key(self, record: Record) -> t.Tuple[t.Any]:
        return tuple(record.get(field.title) for field in self.fields)

    def add_value(self, record: Record):
        key = self._get_key(record)
        self._values.add(key)
