from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import data_source, domain_names


class DomainName(DataType):
    @property
    def value(self):
        return next(data_source(domain_names))
