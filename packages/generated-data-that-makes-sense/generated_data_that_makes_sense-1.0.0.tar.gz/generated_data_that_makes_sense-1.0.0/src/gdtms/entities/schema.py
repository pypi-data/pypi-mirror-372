import typing as t

from gdtms.entities.table import Table
from gdtms.views.view import View


class Schema:
    def __init__(self) -> None:
        self.tables: t.List[Table] = []

    def add_table(self, table: Table) -> "Schema":
        table.set_schema(self)
        self.tables.append(table)
        return self

    def add_tables(self, tables: t.List[Table]) -> "Schema":
        for table in tables:
            self.add_table(table)
        return self

    def dump(self, view: View) -> str:
        return view.dump_schema(self)
