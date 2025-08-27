from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import city_names, data_source


class City(DataType):
    @property
    def value(self):
        return next(data_source(city_names))
