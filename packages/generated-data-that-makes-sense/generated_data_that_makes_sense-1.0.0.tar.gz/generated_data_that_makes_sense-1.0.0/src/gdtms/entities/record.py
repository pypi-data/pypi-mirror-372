import typing as t

from gdtms.data_types.data_type import DataType
from gdtms.views.view import View


class Record:
    def __init__(self, table: "Table") -> None:
        self._table: "Table" = table
        self.values: t.Dict[str, DataType] = {}

    def generate(self) -> None:
        for field in self._table.get_fields():
            name = field.title
            value = field.get_value()
            self._add_value(name, value)

    def _add_value(self, name: str, value) -> None:
        self.values[name] = value

    def dump(self, view: View) -> str:
        return view.dump_record(self)

    def get_table(self) -> str:
        return self._table

    def get(self, key: str) -> DataType:
        return self.values[key]
