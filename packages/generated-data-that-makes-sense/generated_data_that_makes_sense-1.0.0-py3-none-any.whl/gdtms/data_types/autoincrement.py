from gdtms.data_types.data_type import DataType


class Autoincrement(DataType):
    @property
    def value(self):
        return self._get_future_id()

    def _get_future_id(self):
        table = self._field.get_table()
        id = table.get_last_inserted_id() + 1
        return id
