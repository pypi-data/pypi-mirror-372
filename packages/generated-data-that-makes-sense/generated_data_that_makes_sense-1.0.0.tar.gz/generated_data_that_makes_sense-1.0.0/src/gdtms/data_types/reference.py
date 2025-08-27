from gdtms.data_types.data_type import DataType


class Reference(DataType):
    def __init__(self, to_table: "Table"):
        self.to_table = to_table

    @property
    def value(self):
        return self.get_random_record_id()

    def get_random_record_id(self) -> int:
        return self.to_table.get_random_record_id()
