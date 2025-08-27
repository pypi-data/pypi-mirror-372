class View:
    def dump_schema(self, schema: "Schema") -> None:
        raise NotImplementedError()

    def dump_table(self, table: "Table") -> None:
        raise NotImplementedError()

    def dump_record(self, record: "Record") -> None:
        raise NotImplementedError()
