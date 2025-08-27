from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import adjectives, data_source


class Adjective(DataType):
    @property
    def value(self):
        return next(data_source(adjectives))
