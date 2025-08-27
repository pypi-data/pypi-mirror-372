from gdtms.data_types.data_type import DataType


class Undefined(DataType):
    @property
    def value(self):
        return None
