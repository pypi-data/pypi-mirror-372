from gdtms.data_types.data_type import DataType
from gdtms.data_types.domain_name import DomainName


class Url(DataType):
    @property
    def value(self):
        return f"https://{DomainName().value}/"
