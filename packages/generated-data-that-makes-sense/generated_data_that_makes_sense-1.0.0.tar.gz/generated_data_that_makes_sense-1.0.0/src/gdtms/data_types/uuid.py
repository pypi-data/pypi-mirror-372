import uuid

from gdtms.data_types.data_type import DataType


class Uuid(DataType):
    @property
    def value(self):
        return str(uuid.uuid4())
