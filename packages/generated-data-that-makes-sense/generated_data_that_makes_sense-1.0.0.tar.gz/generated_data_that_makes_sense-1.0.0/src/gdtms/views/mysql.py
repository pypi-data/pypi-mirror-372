from gdtms.views.view import View


class Mysql(View):
    def dump_schema(self, schema: "Schema") -> None:
        print("-- Schema:")
        for table in schema.tables:
            table.dump(self)

    def dump_table(self, table: "Table") -> None:
        if not table.get_records():
            return
        print(f"-- Table {table.name}:")
        print(f"DELETE FROM `{table.name}`;")
        print(f"INSERT INTO `{table.name}`")
        self.dump_fields(table.fields)
        print("VALUES")
        self.dump_records(table.records)
        print(";")
        table.clean()

    def dump_fields(self, fields) -> None:
        print("(" + ", ".join([f"`{field.title}`" for field in fields]) + ")")

    def dump_records(self, records) -> None:
        comma = False
        for record in records:
            if comma is True:
                print(",")
            else:
                comma = True
            record.dump(self)

    def dump_record(self, record: "Record") -> None:
        print(
            "("
            + ", ".join([self._dump_value(v) for v in record.values.values()])
            + ")",
            end="",
        )

    def _dump_value(self, value):
        if value is None:
            return "NULL"
        elif isinstance(value, int):
            return str(value)
        out = value.replace("'", "\\'")
        return f"'{out}'"
