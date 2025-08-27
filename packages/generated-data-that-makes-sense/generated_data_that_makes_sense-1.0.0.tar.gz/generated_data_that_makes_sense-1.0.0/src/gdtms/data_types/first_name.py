from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import data_source, first_names


class FirstName(DataType):
    @property
    def value(self):
        return next(data_source(first_names))
