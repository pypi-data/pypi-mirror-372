from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import data_source, proverbs


class Proverb(DataType):
    @property
    def value(self):
        return next(data_source(proverbs))
